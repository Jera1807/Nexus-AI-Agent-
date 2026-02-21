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
        "faq": {"keywords": ["preis", "kosten", "öffnungszeiten"]},
        "booking": {"keywords": ["buchen", "termin", "anmeldung"]},
        "cancellation": {"keywords": ["storno", "absagen", "verschieben"]},
    }
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local golden evals")
    parser.add_argument("--questions", default="tests/golden_questions/questions.yaml")
    parser.add_argument("--output", default="eval_report.json")
    args = parser.parse_args()

    questions = load_questions(Path(args.questions))
    report = run_eval_suite(questions, DEFAULT_INTENTS)

    out = Path(args.output)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Eval report written to {out}")
    print(f"Passed: {report['passed']}/{report['total']} ({report['pass_rate']*100:.1f}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
