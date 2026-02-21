from __future__ import annotations

from typing import Protocol

from src.config import Settings
from src.db.supabase import InMemorySupabaseClient


class EventStore(Protocol):
    def insert_event(self, event: object) -> None: ...

    def list_events(self, tenant_id: str | None = None) -> list[dict]: ...


class SupabaseClientPlaceholder:
    """Production adapter placeholder until real Supabase integration lands."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def insert_event(self, event: object) -> None:
        raise NotImplementedError("Supabase adapter is not implemented yet.")

    def list_events(self, tenant_id: str | None = None) -> list[dict]:
        raise NotImplementedError("Supabase adapter is not implemented yet.")


def create_event_store(settings: Settings) -> EventStore:
    if settings.runtime_mode == "local":
        return InMemorySupabaseClient()
    return SupabaseClientPlaceholder(settings)
