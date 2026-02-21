from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AlertRule:
    max_latency_ms: int = 5000
    min_confidence: float = 0.35


@dataclass
class AlertResult:
    triggered: bool
    reasons: list[str]


def evaluate_alert(latency_ms: int, confidence: float, rule: AlertRule | None = None) -> AlertResult:
    effective = rule or AlertRule()
    reasons: list[str] = []

    if latency_ms > effective.max_latency_ms:
        reasons.append("latency_threshold_exceeded")
    if confidence < effective.min_confidence:
        reasons.append("confidence_too_low")

    return AlertResult(triggered=bool(reasons), reasons=reasons)
