from __future__ import annotations

from typing import Any

from src.routing.models import RiskLevel, RoutingDecision, Tier


DEFAULT_INTENT = "fallback"


def classify_with_llm_fallback(message: str, intents_config: dict[str, Any]) -> RoutingDecision:
    """Deterministic stand-in for future LLM classification.

    Keeps API stable while real provider integration is added later.
    """
    _ = message
    intents = intents_config.get("intents", {})

    if DEFAULT_INTENT in intents:
        meta = intents[DEFAULT_INTENT]
        intent = DEFAULT_INTENT
    else:
        intent, meta = next(iter(intents.items()), (DEFAULT_INTENT, {}))

    return RoutingDecision(
        intent=intent,
        tier=Tier(meta.get("default_tier", Tier.TIER_2.value)),
        risk_level=RiskLevel(meta.get("risk_level", RiskLevel.MEDIUM.value)),
        confidence=0.45,
        rationale="llm fallback placeholder decision",
    )
