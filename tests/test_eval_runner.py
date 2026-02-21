from pathlib import Path

from tests.golden_questions.runner import load_questions, run_eval_suite


INTENTS = {
    "intents": {
        "faq": {"keywords": ["öffnungszeiten", "kosten", "preis"]},
        "booking": {"keywords": ["buchen", "termin", "anmelden"]},
        "cancellation": {"keywords": ["absagen", "storno", "verschieben"]},
    }
}


def test_load_questions() -> None:
    questions = load_questions(Path("tests/golden_questions/questions.yaml"))
    assert len(questions) >= 3
    assert "input" in questions[0]


def test_run_eval_suite_returns_report() -> None:
    questions = [
        {"input": "Öffnungszeiten?", "expected_intent": "faq"},
        {"input": "Termin buchen", "expected_intent": "booking"},
    ]
    report = run_eval_suite(questions, INTENTS)

    assert report["total"] == 2
    assert report["passed"] >= 1
    assert "results" in report
