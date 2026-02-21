from src.config import Settings
from src.db.client import SupabaseClientPlaceholder, create_event_store
from src.db.supabase import InMemorySupabaseClient
from src.observability.client import (
    LangfuseCloudClientPlaceholder,
    create_decision_logger,
)
from src.observability.langfuse import InMemoryLangfuseClient


def test_local_runtime_uses_in_memory_adapters() -> None:
    cfg = Settings(runtime_mode="local")

    event_store = create_event_store(cfg)
    logger = create_decision_logger(cfg)

    assert isinstance(event_store, InMemorySupabaseClient)
    assert isinstance(logger, InMemoryLangfuseClient)


def test_production_runtime_uses_placeholders() -> None:
    cfg = Settings(runtime_mode="production", app_env="development")

    event_store = create_event_store(cfg)
    logger = create_decision_logger(cfg)

    assert isinstance(event_store, SupabaseClientPlaceholder)
    assert isinstance(logger, LangfuseCloudClientPlaceholder)
