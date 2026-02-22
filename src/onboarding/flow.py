from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class OnboardingStep(str, Enum):
    PROVIDER = "provider"
    NAME = "name"
    LANGUAGE = "language"
    DONE = "done"


@dataclass
class OnboardingState:
    user_id: str
    step: OnboardingStep = OnboardingStep.PROVIDER
    provider: str | None = None
    name: str | None = None
    language: str | None = None


@dataclass
class OnboardingFlow:
    _state: dict[str, OnboardingState] = field(default_factory=dict)

    def start(self, user_id: str) -> tuple[str, list[str]]:
        self._state[user_id] = OnboardingState(user_id=user_id)
        return (
            "Willkommen bei Nexus! Bitte wähle deinen LLM-Provider:",
            ["openai", "anthropic", "google", "deepseek"],
        )

    def handle_provider(self, user_id: str, provider: str) -> str:
        state = self._state.setdefault(user_id, OnboardingState(user_id=user_id))
        state.provider = provider
        state.step = OnboardingStep.NAME
        return "Super. Wie soll ich dich nennen?"

    def handle_name(self, user_id: str, name: str) -> tuple[str, list[str]]:
        state = self._state.setdefault(user_id, OnboardingState(user_id=user_id))
        state.name = name.strip()
        state.step = OnboardingStep.LANGUAGE
        return ("Welche Sprache bevorzugst du?", ["de", "en", "both"])

    def handle_language(self, user_id: str, language: str) -> str:
        state = self._state.setdefault(user_id, OnboardingState(user_id=user_id))
        state.language = language
        state.step = OnboardingStep.DONE
        return (
            f"Onboarding abgeschlossen ✅\n"
            f"Provider: {state.provider}\n"
            f"Name: {state.name}\n"
            f"Sprache: {state.language}\n"
            f"Nutze /help, /connect <plugin>, /costs, /facts."
        )

    def get_state(self, user_id: str) -> OnboardingState | None:
        return self._state.get(user_id)
