from __future__ import annotations

from dataclasses import asdict

from src.db.models import ConversationEvent


class InMemorySupabaseClient:
    def __init__(self) -> None:
        self._events: list[ConversationEvent] = []

    def insert_event(self, event: ConversationEvent) -> None:
        self._events.append(event)

    def list_events(self, tenant_id: str | None = None) -> list[dict]:
        rows = self._events
        if tenant_id is not None:
            rows = [item for item in rows if item.tenant_id == tenant_id]
        return [asdict(item) for item in rows]
