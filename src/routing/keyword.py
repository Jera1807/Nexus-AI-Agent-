from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from src.routing.models import RiskLevel, RoutingDecision, Tier

WORD_BOUNDARY_TEMPLATE = r"(?<!\w){token}(?!\w)"


@lru_cache(maxsize=1024)
def _compile_keyword_pattern(keyword: str) -> re.Pattern[str]:
    escaped = re.escape(keyword.strip().lower())
    if not escaped:
        return re.compile(r"a^")
    pattern = WORD_BOUNDARY_TEMPLATE.format(token=escaped)
    return re.compile(pattern, flags=re.IGNORECASE)


def keyword_route(message: str, intents_config: dict[str, Any]) -> RoutingDecision | None:
    text = message.lower()
    intents = intents_config.get("intents", {})

    best_intent: str | None = None
    best_score = 0.0
    best_match_count = 0

    for intent_name, intent_meta in intents.items():
        keywords = intent_meta.get("keywords", [])
        if not keywords:
            continue

        patterns = [_compile_keyword_pattern(str(keyword)) for keyword in keywords]
        matches = sum(1 for pattern in patterns if pattern.search(text))
        if matches == 0:
            continue

        score = matches / len(patterns)
        if score > best_score:
            best_score = score
            best_intent = intent_name
            best_match_count = matches

    if not best_intent:
        return None

    meta = intents[best_intent]
    tier = Tier(meta.get("default_tier", Tier.TIER_2.value))
    risk_level = RiskLevel(meta.get("risk_level", RiskLevel.MEDIUM.value))

    rationale = f"keyword match: {best_match_count} Treffer für Intent '{best_intent}'"
    return RoutingDecision(
        intent=best_intent,
        tier=tier,
        risk_level=risk_level,
        confidence=round(min(0.95, 0.4 + best_score), 3),
        rationale=rationale,
    )
