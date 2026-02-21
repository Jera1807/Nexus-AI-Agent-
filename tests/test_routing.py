import pytest

from src.routing.confidence import clamp_confidence, combine_confidence, confidence_label
from src.routing.keyword import keyword_route
from src.routing.llm_classifier import classify_with_llm_fallback
from src.routing.semantic import semantic_route


def test_keyword_route_matches_booking_intent():
    intents = {
        "intents": {
            "booking": {
                "keywords": ["book", "termin", "appointment"],
                "default_tier": "tier_2",
                "risk_level": "medium",
            }
        }
    }

    decision = keyword_route("Kann ich einen Termin buchen?", intents)

    assert decision is not None
    assert decision.intent == "booking"
    assert decision.tier.value == "tier_2"
    assert decision.risk_level.value == "medium"
    assert decision.confidence > 0.0


def test_keyword_route_returns_none_for_unknown_message():
    intents = {"intents": {"faq": {"keywords": ["price"]}}}

    decision = keyword_route("Ich mag Katzen", intents)

    assert decision is None


def test_semantic_route_uses_examples():
    intents = {
        "intents": {
            "consultation": {
                "examples": [
                    "Ich brauche eine Beratung zur Nagelmodellage",
                    "Welche Behandlung passt zu mir?",
                ],
                "default_tier": "tier_2",
                "risk_level": "medium",
            }
        }
    }

    decision = semantic_route("Brauche Beratung welche Behandlung passt", intents)

    assert decision is not None
    assert decision.intent == "consultation"
    assert decision.confidence >= 0.35


def test_semantic_route_none_for_empty_overlap():
    intents = {"intents": {"faq": {"examples": ["Öffnungszeiten und Preise"]}}}

    assert semantic_route("Ich möchte über Fußball reden", intents) is None


def test_confidence_helpers():
    assert clamp_confidence(1.7) == 1.0
    assert combine_confidence(0.9, 0.1, weights=[2, 1]) == pytest.approx((0.9 * 2 + 0.1) / 3)
    assert confidence_label(0.81) == "high"
    assert confidence_label(0.6) == "medium"
    assert confidence_label(0.3) == "low"


def test_llm_classifier_placeholder_returns_stable_decision():
    intents = {
        "intents": {
            "fallback": {"default_tier": "tier_3", "risk_level": "high"},
            "booking": {"default_tier": "tier_2", "risk_level": "medium"},
        }
    }

    decision = classify_with_llm_fallback("irgendwas", intents)

    assert decision.intent == "fallback"
    assert decision.tier.value == "tier_3"
    assert decision.risk_level.value == "high"
