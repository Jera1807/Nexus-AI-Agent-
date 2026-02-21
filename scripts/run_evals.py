from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.golden_questions.runner import load_questions, run_eval_suite


DEFAULT_INTENTS = {
    "intents": {
        "faq": {"keywords": ["preis", "kosten", "öffnungszeiten"], "default_tier": "tier_1"},
        "booking": {"keywords": ["buchen", "termin", "anmeldung"], "default_tier": "tier_2"},
        "cancellation": {"keywords": ["storno", "absagen", "verschieben"], "default_tier": "tier_2"},
    }
}


def _select_questions(questions: list[dict], suite: str) -> list[dict]:
    if suite == "smoke":
        return questions[: min(5, len(questions))]
    return questions


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local golden evals")
    parser.add_argument("--questions", default="tests/golden_questions/questions.yaml")
    parser.add_argument("--output", default="eval_report.json")
    parser.add_argument("--suite", default="golden", choices=["golden", "smoke"])
    parser.add_argument("--tenant", default="example_tenant")
    args = parser.parse_args()

    questions = load_questions(Path(args.questions))
    selected = _select_questions(questions, suite=args.suite)
    report = run_eval_suite(selected, DEFAULT_INTENTS)
    report["suite"] = args.suite
    report["tenant"] = args.tenant

    out = Path(args.output)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Eval report written to {out}")
    print(f"Suite: {args.suite}, Tenant: {args.tenant}")
    print(f"Passed: {report['passed']}/{report['total']} ({report['pass_rate']*100:.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
