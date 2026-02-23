from __future__ import annotations

import base64
import binascii
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class UnifiedMessage(BaseModel):
    channel: str
    sender_id: str
    tenant_id: str
    text: str
    message_id: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)
    voice_audio: bytes | None = None
    is_subagent_message: bool = False
    subagent_id: str | None = None


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
    voice_audio: bytes | None = None
    voice = payload.get("voice")
    if isinstance(voice, dict) and isinstance(voice.get("audio_base64"), str):
        try:
            voice_audio = base64.b64decode(voice["audio_base64"], validate=True)
        except (binascii.Error, ValueError):
            voice_audio = None

    callback_data = None
    if isinstance(payload.get("callback_query"), dict):
        callback_data = payload["callback_query"].get("data")

    media = {
        "photos": payload.get("photo", []),
        "document": payload.get("document"),
    }

    return UnifiedMessage(
        channel="telegram",
        sender_id=str(payload.get("from", {}).get("id", "")),
        tenant_id=tenant_id,
        text=str(callback_data or payload.get("text", "")),
        message_id=str(payload.get("message_id", "")) or None,
        metadata={"chat_id": payload.get("chat", {}).get("id"), "media": media},
        voice_audio=voice_audio,
    )
