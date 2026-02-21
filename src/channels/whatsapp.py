from __future__ import annotations

from src.channels.base import BaseChannel, build_disclosure
from src.channels.message import UnifiedMessage


class WhatsAppChannel(BaseChannel):
    def __init__(self, default_tenant_id: str = "example_tenant") -> None:
        self.default_tenant_id = default_tenant_id

    def receive(self, payload: dict) -> UnifiedMessage:
        return UnifiedMessage(
            channel="whatsapp",
            sender_id=str(payload.get("from", "")),
            tenant_id=str(payload.get("tenant_id") or self.default_tenant_id),
            text=str(payload.get("text", "")),
            message_id=str(payload.get("id", "")) or None,
            metadata={"bridge": "baileys"},
        )

    def format_response(self, text: str, tenant_name: str) -> str:
        return f"{build_disclosure(tenant_name)}\n{text}"
