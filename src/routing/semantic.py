from __future__ import annotations

import re
from typing import Any

from src.routing.confidence import clamp_confidence
from src.routing.models import GroundingMode, RiskLevel, RoutingDecision, Tier

TOKEN_PATTERN = re.compile(r"\w+", flags=re.UNICODE)


def _tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_PATTERN.findall(text)}


def semantic_route(message: str, intents_config: dict[str, Any]) -> RoutingDecision | None:
    """Simple lexical-overlap semantic fallback.

    Uses intent `examples` first; if absent, falls back to `keywords`.
    """
    message_tokens = _tokenize(message)
    if not message_tokens:
        return None

    intents = intents_config.get("intents", {})
    best_intent: str | None = None
    best_overlap = 0.0

    for intent_name, intent_meta in intents.items():
        seed_phrases = intent_meta.get("examples") or intent_meta.get("keywords") or []
        if not seed_phrases:
            continue

        candidate_tokens: set[str] = set()
        for phrase in seed_phrases:
            candidate_tokens.update(_tokenize(str(phrase)))

        if not candidate_tokens:
            continue

        overlap = len(message_tokens & candidate_tokens) / len(candidate_tokens)
        if overlap > best_overlap:
            best_overlap = overlap
            best_intent = intent_name

    if not best_intent or best_overlap <= 0:
        return None

    meta = intents[best_intent]
    tier = Tier(meta.get("default_tier", Tier.TIER_2.value))
    return RoutingDecision(
        intent=best_intent,
        tier=tier,
        risk_level=RiskLevel(meta.get("risk_level", RiskLevel.MEDIUM.value)),
        confidence=clamp_confidence(0.35 + best_overlap),
        rationale=f"semantic overlap match for intent '{best_intent}'",
        grounding_mode=GroundingMode(meta.get("grounding_mode", GroundingMode.OPEN.value)),
        plugins_to_load=list(meta.get("plugins", [])),
        should_delegate=tier == Tier.TIER_3,
    )
