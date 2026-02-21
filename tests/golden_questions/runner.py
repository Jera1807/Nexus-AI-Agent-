from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

from src.routing.keyword import keyword_route


@dataclass
class EvalResult:
    input_text: str
    expected_intent: str
    predicted_intent: str | None
    passed: bool


def load_questions(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(raw) or {}
    else:
        data = json.loads(raw or "{}")
    return data.get("questions", [])


def run_eval_suite(questions: list[dict[str, Any]], intents_config: dict[str, Any]) -> dict[str, Any]:
    results: list[EvalResult] = []

    for item in questions:
        text = item.get("input", "")
        expected = item.get("expected_intent")
        decision = keyword_route(text, intents_config)
        predicted = decision.intent if decision else None

        results.append(
            EvalResult(
                input_text=text,
                expected_intent=expected,
                predicted_intent=predicted,
                passed=(predicted == expected),
            )
        )

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = (passed / total) if total else 0.0

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(pass_rate, 3),
        "results": [r.__dict__ for r in results],
    }
