from __future__ import annotations

import json
import time
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
    expected_intent: str | None
    predicted_intent: str | None
    expected_tier: str | None
    predicted_tier: str | None
    latency_ms: int
    citations_present: bool
    checks: dict[str, bool]
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
        text = str(item.get("input", ""))
        expected_intent = item.get("expected_intent")
        expected_tier = item.get("expected_tier")
        must_have_citations = bool(item.get("must_have_citations", False))
        max_latency_ms = int(item.get("max_latency_ms", 2_000))

        t0 = time.perf_counter()
        decision = keyword_route(text, intents_config)
        latency_ms = int((time.perf_counter() - t0) * 1000)

        predicted_intent = decision.intent if decision else None
        predicted_tier = decision.tier.value if decision else None

        # We currently do not generate answer citations in this runner baseline.
        citations_present = False

        checks = {
            "intent_match": (expected_intent is None or predicted_intent == expected_intent),
            "tier_match": (expected_tier is None or predicted_tier == expected_tier),
            "latency_ok": latency_ms <= max_latency_ms,
            "citations_ok": (not must_have_citations) or citations_present,
        }
        passed = all(checks.values())

        results.append(
            EvalResult(
                input_text=text,
                expected_intent=expected_intent,
                predicted_intent=predicted_intent,
                expected_tier=expected_tier,
                predicted_tier=predicted_tier,
                latency_ms=latency_ms,
                citations_present=citations_present,
                checks=checks,
                passed=passed,
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
