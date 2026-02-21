from __future__ import annotations

from typing import Any

from src.routing.keyword import keyword_route
from src.routing.llm_classifier import classify_with_llm_fallback
from src.routing.models import RiskLevel, RoutingDecision
from src.routing.semantic import semantic_route
from src.tenant.models import TenantContext
from src.tools.registry import ToolRegistry


def route(message: str, tenant_context: TenantContext) -> RoutingDecision:
    """Run the 4-step routing pipeline: keyword -> semantic -> llm_classifier.

    After classification, enriches the decision with tenant-specific
    risk_mapping overrides and tools_to_load.
    """
    intents_config = tenant_context.config.intents

    # Step 1: Keyword pre-filter (free, <1ms)
    decision = keyword_route(message, intents_config)

    # Step 2: Semantic router (free, <10ms)
    if decision is None:
        decision = semantic_route(message, intents_config)

    # Step 3: LLM classifier fallback (only for ambiguous queries)
    if decision is None:
        decision = classify_with_llm_fallback(message, intents_config)

    # Apply tenant-specific risk mapping overrides
    risk_override = tenant_context.risk_mapping.get(decision.intent)
    if risk_override:
        try:
            decision = decision.model_copy(update={
                "risk_level": RiskLevel(risk_override),
                "requires_confirmation": RiskLevel(risk_override) in {RiskLevel.HIGH, RiskLevel.CRITICAL},
            })
        except ValueError:
            pass  # Invalid risk level in config, keep original

    # Attach tools_to_load from tenant tool registry
    registry = ToolRegistry(tenant_context.config.tools)
    tools_for_intent = registry.get_tools_for_intent(decision.intent)
    decision = decision.model_copy(update={
        "tools_to_load": [t["name"] for t in tools_for_intent],
    })

    return decision
