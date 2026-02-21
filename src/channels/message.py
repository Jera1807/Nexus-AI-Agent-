from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class UnifiedMessage:
    channel: str
    sender_id: str
    tenant_id: str
    text: str
    message_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


def from_web_payload(payload: dict[str, Any]) -> UnifiedMessage:
    return UnifiedMessage(
        channel="web",
        sender_id=str(payload.get("sender_id", "anonymous")),
        tenant_id=str(payload.get("tenant_id", "example_tenant")),
        text=str(payload.get("text", "")),
        message_id=payload.get("message_id"),
        metadata={"source": "websocket"},
    )


def from_telegram_payload(payload: dict[str, Any], tenant_id: str) -> UnifiedMessage:
    return UnifiedMessage(
        channel="telegram",
        sender_id=str(payload.get("from", {}).get("id", "")),
        tenant_id=tenant_id,
        text=str(payload.get("text", "")),
        message_id=str(payload.get("message_id", "")) or None,
        metadata={"chat_id": payload.get("chat", {}).get("id")},
    )
