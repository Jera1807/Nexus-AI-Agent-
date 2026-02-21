from __future__ import annotations

from src.channels.base import BaseChannel, build_disclosure
from src.channels.message import UnifiedMessage, from_telegram_payload


class TelegramChannel(BaseChannel):
    def __init__(self, default_tenant_id: str = "example_tenant") -> None:
        self.default_tenant_id = default_tenant_id

    def receive(self, payload: dict) -> UnifiedMessage:
        tenant_id = str(payload.get("tenant_id") or self.default_tenant_id)
        return from_telegram_payload(payload, tenant_id=tenant_id)

    def format_response(self, text: str, tenant_name: str) -> str:
        return f"{build_disclosure(tenant_name)}\n{text}"
