from pathlib import Path

from tests.golden_questions.runner import load_questions, run_eval_suite


INTENTS = {
    "intents": {
        "faq": {"keywords": ["öffnungszeiten", "kosten", "preis"], "default_tier": "tier_1"},
        "booking": {"keywords": ["buchen", "termin", "anmelden"], "default_tier": "tier_2"},
        "cancellation": {"keywords": ["absagen", "storno", "verschieben"], "default_tier": "tier_2"},
    }
}


def test_load_questions() -> None:
    questions = load_questions(Path("tests/golden_questions/questions.yaml"))
    assert len(questions) >= 3
    assert "input" in questions[0]


def test_run_eval_suite_returns_report_with_checks() -> None:
    questions = [
        {
            "input": "Öffnungszeiten?",
            "expected_intent": "faq",
            "expected_tier": "tier_1",
            "must_have_citations": False,
            "max_latency_ms": 1000,
        },
        {
            "input": "Termin buchen",
            "expected_intent": "booking",
            "expected_tier": "tier_2",
            "must_have_citations": False,
            "max_latency_ms": 1000,
        },
    ]
    report = run_eval_suite(questions, INTENTS)

    assert report["total"] == 2
    assert report["passed"] >= 1
    assert "results" in report
    assert "checks" in report["results"][0]
    assert "tier_match" in report["results"][0]["checks"]
