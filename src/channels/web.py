from __future__ import annotations

from src.channels.base import BaseChannel, build_disclosure
from src.channels.message import UnifiedMessage, from_web_payload


class WebChannel(BaseChannel):
    def receive(self, payload: dict) -> UnifiedMessage:
        return from_web_payload(payload)

    def format_response(self, text: str, tenant_name: str) -> str:
        return f"{build_disclosure(tenant_name)}\n\n{text}"
