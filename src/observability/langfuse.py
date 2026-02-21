from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from src.observability.pii import redact_pii


@dataclass
class DecisionLog:
    request_id: str
    tenant_id: str
    channel: str
    sender_id: str
    input_text: str
    redacted_input_text: str
    predicted_intent: str
    tier: str
    risk_level: str
    confidence: float
    tools_considered: list[str]
    tools_called: list[str]
    grounding_passed: bool
    citations: list[str]
    response_text: str
    latency_ms: int
    token_in: int
    token_out: int
    created_at: str


class InMemoryLangfuseClient:
    """Small local stand-in for Langfuse decision logging."""

    def __init__(self) -> None:
        self._logs: list[DecisionLog] = []

    def log_decision(self, payload: dict[str, Any]) -> DecisionLog:
        input_text = str(payload.get("input_text", ""))
        redacted = redact_pii(input_text)

        log = DecisionLog(
            request_id=str(payload.get("request_id", "")),
            tenant_id=str(payload.get("tenant_id", "")),
            channel=str(payload.get("channel", "unknown")),
            sender_id=str(payload.get("sender_id", "")),
            input_text=input_text,
            redacted_input_text=redacted.text,
            predicted_intent=str(payload.get("predicted_intent", "fallback")),
            tier=str(payload.get("tier", "tier_2")),
            risk_level=str(payload.get("risk_level", "medium")),
            confidence=float(payload.get("confidence", 0.0)),
            tools_considered=list(payload.get("tools_considered", [])),
            tools_called=list(payload.get("tools_called", [])),
            grounding_passed=bool(payload.get("grounding_passed", False)),
            citations=list(payload.get("citations", [])),
            response_text=str(payload.get("response_text", "")),
            latency_ms=int(payload.get("latency_ms", 0)),
            token_in=int(payload.get("token_in", 0)),
            token_out=int(payload.get("token_out", 0)),
            created_at=str(payload.get("created_at", datetime.now(tz=timezone.utc).isoformat())),
        )
        self._logs.append(log)
        return log

    def logs(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self._logs]
