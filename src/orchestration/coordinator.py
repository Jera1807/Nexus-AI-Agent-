from __future__ import annotations

from src.agent.loop import AgentLoop
from src.agent.structured import AgentResponse
from src.channels.message import UnifiedMessage
from src.orchestration.budget import BudgetAgent
from src.orchestration.guardian import GuardianAgent, GuardianOutcome
from src.orchestration.manager import ManagerAgent
from src.orchestration.specialists import CoderAgent, ContextBundle, OpsAgent, ResearchAgent, WriterAgent
from src.routing.models import RiskLevel, RoutingDecision, Tier


class Coordinator:
    def __init__(self) -> None:
        self.manager = ManagerAgent()
        self.budget = BudgetAgent()
        self.guardian = GuardianAgent()
        self.loop = AgentLoop()
        self.specialists = [ResearchAgent(), CoderAgent(), WriterAgent(), OpsAgent()]

    def _simple_route(self, text: str) -> RoutingDecision:
        lowered = text.lower()
        if any(token in lowered for token in ["mail", "workflow", "calendar", "server"]):
            return RoutingDecision(
                intent="automation",
                tier=Tier.TIER_2,
                risk_level=RiskLevel.MEDIUM,
                confidence=0.5,
                rationale="complex keyword",
                should_delegate=True,
            )
        return RoutingDecision(
            intent="general",
            tier=Tier.TIER_1,
            risk_level=RiskLevel.LOW,
            confidence=0.9,
            rationale="simple greeting",
            should_delegate=False,
        )

    def process(self, message: UnifiedMessage) -> AgentResponse:
        decision = self._simple_route(message.text)

        # Apply security/budget checks even on fast path.
        guardian_verdict = self.guardian.review(
            tool_name="agent_response",
            args={"query": message.text},
            risk_level=decision.risk_level.value,
        )
        if guardian_verdict.outcome == GuardianOutcome.BLOCKED:
            return AgentResponse(text="Anfrage wurde aus Sicherheitsgründen blockiert.", intent=decision.intent, confidence=0.9, citations=[])

        selection = self.budget.select_model(decision.tier.value, message.text)

        if not decision.should_delegate:
            result = self.loop.process(
                {
                    "request_id": message.message_id or "req",
                    "tenant_id": message.tenant_id,
                    "sender_id": message.sender_id,
                    "channel": message.channel,
                    "text": message.text,
                    "intent": decision.intent,
                    "tier": selection.model_name,
                    "max_tokens": selection.max_tokens,
                }
            )
            return AgentResponse(text=result["text"], intent=result["intent"], confidence=0.8, citations=[])

        request_id = message.message_id or "req"
        tasks = self.manager.decompose(message.text, decision, request_id=request_id)
        context = ContextBundle(request_id=request_id, tenant_id=message.tenant_id, channel=message.channel, sender_id=message.sender_id)

        results = []
        for i, task in enumerate(tasks):
            specialist = self.specialists[i % len(self.specialists)]
            results.append(specialist.execute(task, context))

        return self.manager.assemble(results, decision.intent)
