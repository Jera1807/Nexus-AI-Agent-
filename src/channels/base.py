from __future__ import annotations

from abc import ABC, abstractmethod

from src.channels.message import UnifiedMessage


class BaseChannel(ABC):
    @abstractmethod
    def receive(self, payload: dict) -> UnifiedMessage:  # pragma: no cover - interface method
        raise NotImplementedError

    @abstractmethod
    def format_response(self, text: str, tenant_name: str) -> str:  # pragma: no cover
        raise NotImplementedError


def build_disclosure(tenant_name: str) -> str:
    return f"Hinweis: Du schreibst mit dem KI-Assistenten von {tenant_name}."
