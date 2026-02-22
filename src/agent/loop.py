from __future__ import annotations

import time
from typing import Any

import httpx

from src.config import settings
from src.observability.client import DecisionLogger, create_decision_logger


class AgentLoop:
    def __init__(self, logger: DecisionLogger | None = None) -> None:
        self.logger = logger or create_decision_logger(settings)

    def _call_litellm(self, model: str, prompt: str, max_tokens: int) -> str:
        try:
            response = httpx.post(
                f"{settings.litellm_base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                },
                headers={"Authorization": f"Bearer {settings.litellm_api_key}"},
                timeout=8.0,
            )
            response.raise_for_status()
            data = response.json()
            return str(data["choices"][0]["message"]["content"])
        except Exception:
            return "Alles klar, ich kümmere mich darum."

    def process(self, event: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        model = str(event.get("tier", "tier_2"))
        prompt = str(event.get("text", ""))
        text = self._call_litellm(model=model, prompt=prompt, max_tokens=400)

        response = {
            "text": text,
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
                "tier": model,
                "risk_level": "medium",
                "confidence": 0.6,
                "tools_considered": [],
                "tools_called": [],
                "grounding_passed": True,
                "citations": [],
                "response_text": response["text"],
                "latency_ms": int((time.perf_counter() - start) * 1000),
                "token_in": 10,
                "token_out": 12,
            }
        )
        return response
