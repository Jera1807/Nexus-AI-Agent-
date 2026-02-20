from src.routing.keyword import keyword_route


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
