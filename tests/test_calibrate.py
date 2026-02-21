from scripts.calibrate import analyze_decisions


def test_analyze_decisions_counts_and_recommends_higher_threshold() -> None:
    records = [
        {"expected_intent": "faq", "predicted_intent": "booking", "confidence": 0.2, "escalated": False},
        {"expected_intent": "faq", "predicted_intent": "booking", "confidence": 0.3, "escalated": False},
        {"expected_intent": "faq", "predicted_intent": "faq", "confidence": 0.9, "escalated": True},
    ]
    report = analyze_decisions(records, current_low_conf_threshold=0.35)

    assert report.false_passes == 2
    assert report.false_escalations == 1
    assert report.recommended_low_conf_threshold > 0.35


def test_analyze_decisions_recommends_lower_threshold_when_over_escalating() -> None:
    records = [
        {"expected_intent": "faq", "predicted_intent": "faq", "confidence": 0.8, "escalated": True},
        {"expected_intent": "booking", "predicted_intent": "booking", "confidence": 0.7, "escalated": True},
    ]
    report = analyze_decisions(records, current_low_conf_threshold=0.35)

    assert report.false_passes == 0
    assert report.false_escalations == 2
    assert report.recommended_low_conf_threshold < 0.35
