from __future__ import annotations

from typing import Any

from src.observability.client import DecisionLogger, create_decision_logger
from src.config import settings


class AgentLoop:
    def __init__(self, logger: DecisionLogger | None = None) -> None:
        self.logger = logger or create_decision_logger(settings)

    def process(self, event: dict[str, Any]) -> dict[str, Any]:
        response = {
            "text": "Alles klar, ich kümmere mich darum.",
            "intent": event.get("intent", "fallback"),
        }
        self.logger.log_decision(
            {
                "request_id": event.get("request_id", ""),
                "tenant_id": event.get("tenant_id", ""),
                "channel": event.get("channel", "web"),
                "sender_id": event.get("sender_id", ""),
                "input_text": event.get("text", ""),
                "predicted_intent": response["intent"],
                "tier": "tier_2",
                "risk_level": "medium",
                "confidence": 0.6,
                "tools_considered": [],
                "tools_called": [],
                "grounding_passed": True,
                "citations": [],
                "response_text": response["text"],
                "latency_ms": 100,
                "token_in": 10,
                "token_out": 12,
            }
        )
        return response
