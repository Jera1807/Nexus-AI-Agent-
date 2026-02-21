from __future__ import annotations

from typing import Protocol

from src.config import Settings
from src.observability.langfuse import InMemoryLangfuseClient


class DecisionLogger(Protocol):
    def log_decision(self, payload: dict) -> object: ...


class LangfuseCloudClientPlaceholder:
    """Production adapter placeholder until real Langfuse SDK wiring lands."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def log_decision(self, payload: dict) -> object:
        raise NotImplementedError("Langfuse cloud adapter is not implemented yet.")


def create_decision_logger(settings: Settings) -> DecisionLogger:
    if settings.runtime_mode == "local":
        return InMemoryLangfuseClient()
    return LangfuseCloudClientPlaceholder(settings)
