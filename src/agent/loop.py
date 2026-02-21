from __future__ import annotations

import time
from typing import Any
from uuid import uuid4

import httpx

from src.agent.prompt import build_system_prompt
from src.agent.structured import AgentResponse, Citation, DecisionLog
from src.config import settings
from src.grounding.citations import extract_citations
from src.grounding.entity_registry import EntityRegistry
from src.grounding.repair import repair_or_fallback
from src.memory.context import ContextPackage, build_context_package
from src.memory.semantic import SemanticMemoryIndex
from src.memory.summary import summarize_turns
from src.memory.working import WorkingMemoryStore
from src.observability.langfuse import InMemoryLangfuseClient
from src.routing import route
from src.routing.confidence import combine_confidence
from src.routing.models import RoutingDecision, Tier
from src.tenant.models import TenantContext
from src.tools.registry import ToolRegistry

MAX_LOOPS = 3
TIMEOUT_SECONDS = 30

TIER_TO_MODEL = {
    Tier.TIER_1: "tier_1",
    Tier.TIER_2: "tier_2",
    Tier.TIER_3: "tier_3",
}


class AgentLoop:
    """ReAct agent loop that integrates routing, memory, grounding, and LLM."""

    def __init__(
        self,
        working_memory: WorkingMemoryStore | None = None,
        semantic_index: SemanticMemoryIndex | None = None,
        entity_registry: EntityRegistry | None = None,
        logger: InMemoryLangfuseClient | None = None,
    ) -> None:
        self.working_memory = working_memory or WorkingMemoryStore()
        self.semantic_index = semantic_index or SemanticMemoryIndex()
        self.entity_registry = entity_registry or EntityRegistry(tenant_id="default")
        self.logger = logger or InMemoryLangfuseClient()

    def process(
        self,
        event: dict[str, Any],
        tenant_context: TenantContext | None = None,
    ) -> AgentResponse:
        """Process a single user message through the full pipeline."""
        request_id = event.get("request_id", str(uuid4()))
        tenant_id = event.get("tenant_id", "")
        sender_id = event.get("sender_id", "")
        channel = event.get("channel", "web")
        text = event.get("text", "")
        session_id = f"{tenant_id}:{sender_id}"

        t0 = time.perf_counter()

        # 1. Routing
        if tenant_context is not None:
            decision = route(text, tenant_context)
        else:
            decision = RoutingDecision(
                intent=event.get("intent", "fallback"),
                tier=Tier.TIER_2,
                risk_level="medium",
                confidence=0.5,
                source="keyword",
            )

        # 2. Memory: store turn + assemble context
        self.working_memory.append(session_id, "user", text)
        turns = self.working_memory.get(session_id)
        summary = summarize_turns(turns)
        snippets = self.semantic_index.search(text, top_k=3)
        context_pkg = build_context_package(
            working_turns=turns,
            summary=summary,
            semantic_snippets=snippets,
        )

        # 3. Build system prompt with tools
        tool_schemas: list[dict[str, Any]] = []
        if tenant_context:
            registry = ToolRegistry(tenant_context.config.tools)
            tool_schemas = registry.get_tools_for_intent(decision.intent)

        context_text = self._format_context(context_pkg)
        system_prompt = ""
        if tenant_context:
            system_prompt = build_system_prompt(tenant_context, tool_schemas, context_text)

        # 4. LLM call (with escalation fallback)
        answer_text = self._call_llm(text, system_prompt, decision, context_pkg)

        # 5. Grounding validation
        grounding_passed = True
        citations: list[str] = []
        if self.entity_registry.valid_citations:
            answer_text, grounding_result = repair_or_fallback(
                answer_text, self.entity_registry
            )
            grounding_passed = grounding_result.passed
            citations = grounding_result.citations

        # 6. Heuristic confidence (spec formula)
        rag_score = max((s.score for s in snippets), default=0.0)
        rag_coverage = min(1.0, len(snippets) / 3.0) if snippets else 0.0
        tool_success = 1.0
        validator_pass = 1.0 if grounding_passed else 0.0
        citation_coverage = 1.0 if citations else 0.0

        final_confidence = combine_confidence(
            rag_score, rag_coverage, tool_success, validator_pass, citation_coverage,
            weights=[0.30, 0.10, 0.20, 0.25, 0.15],
        )

        # Auto-low: hard facts without citations → 0.3
        extracted = extract_citations(answer_text)
        if not extracted and self.entity_registry.valid_citations:
            final_confidence = min(final_confidence, 0.3)

        # 7. Store assistant turn
        self.working_memory.append(session_id, "assistant", answer_text)

        latency_ms = int((time.perf_counter() - t0) * 1000)

        # 8. Decision log
        log = DecisionLog(
            request_id=request_id,
            tenant_id=tenant_id,
            channel=channel,
            sender_id=sender_id,
            input_text=text,
            predicted_intent=decision.intent,
            tier=decision.tier.value,
            risk_level=decision.risk_level.value if hasattr(decision.risk_level, "value") else str(decision.risk_level),
            confidence=round(final_confidence, 3),
            source=decision.source,
            tools_considered=[t.get("name", "") for t in tool_schemas],
            tools_called=[],
            grounding_passed=grounding_passed,
            citations=citations,
            response_text=answer_text,
            latency_ms=latency_ms,
        )

        self.logger.log_decision(log.model_dump())

        # 9. Build response
        citation_objects = [Citation(id=cid, fact="", source="kb") for cid in citations]

        return AgentResponse(
            text=answer_text,
            citations=citation_objects,
            confidence=round(final_confidence, 3),
            intent=decision.intent,
            fallback_text=answer_text,
            decision_log=log,
        )

    def _call_llm(
        self,
        user_text: str,
        system_prompt: str,
        decision: RoutingDecision,
        context: ContextPackage,
    ) -> str:
        """Call LiteLLM proxy. Falls back to a canned response if unavailable."""
        model = TIER_TO_MODEL.get(decision.tier, "tier_2")

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        for turn in context.working_turns:
            messages.append({"role": turn.role, "content": turn.content})

        if not messages or messages[-1].get("content") != user_text:
            messages.append({"role": "user", "content": user_text})

        try:
            resp = httpx.post(
                f"{settings.litellm_base_url}/chat/completions",
                json={"model": model, "messages": messages, "max_tokens": 800},
                headers={"Authorization": f"Bearer {settings.litellm_api_key}"},
                timeout=TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception:
            # Offline / dev mode fallback
            return f"Ich helfe dir gerne weiter. (Intent: {decision.intent}, Tier: {decision.tier.value})"

    def _format_context(self, pkg: ContextPackage) -> str:
        """Format a ContextPackage into a string for prompt injection."""
        parts: list[str] = []
        if pkg.working_turns:
            turn_lines = [f"{t.role}: {t.content}" for t in pkg.working_turns[-4:]]
            parts.append("Letzte Nachrichten:\n" + "\n".join(turn_lines))
        if pkg.summary:
            parts.append(f"Zusammenfassung: {pkg.summary}")
        if pkg.semantic_snippets:
            snippet_lines = [f"- [{s.snippet_id}] {s.text}" for s in pkg.semantic_snippets]
            parts.append("Relevantes Wissen:\n" + "\n".join(snippet_lines))
        return "\n\n".join(parts)
