from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.channels.base import BaseChannel, build_disclosure
from src.channels.message import UnifiedMessage, from_telegram_payload
from src.channels.voice import VoicePipeline
from src.onboarding.flow import OnboardingFlow, OnboardingStep
from src.orchestration.budget import BudgetAgent
from src.orchestration.coordinator import Coordinator


@dataclass
class TelegramReply:
    text: str
    voice: bytes | None = None
    keyboard: list[str] | None = None


class TelegramChannel(BaseChannel):
    def __init__(self, default_tenant_id: str = "example_tenant") -> None:
        self.default_tenant_id = default_tenant_id

    def receive(self, payload: dict) -> UnifiedMessage:
        tenant_id = str(payload.get("tenant_id") or self.default_tenant_id)
        return from_telegram_payload(payload, tenant_id=tenant_id)

    def format_response(self, text: str, tenant_name: str) -> str:
        return f"{build_disclosure(tenant_name)}\n{text}"


class TelegramBotService:
    def __init__(self, coordinator: Coordinator | None = None) -> None:
        self.channel = TelegramChannel()
        self.coordinator = coordinator or Coordinator()
        self.voice = VoicePipeline()
        self.onboarding = OnboardingFlow()
        self.budget = BudgetAgent()

    def handle_update(self, payload: dict[str, Any]) -> TelegramReply:
        text = str(payload.get("text", "")).strip()
        sender_id = str(payload.get("from", {}).get("id", payload.get("sender_id", "")))

        if text.startswith("/start"):
            prompt, options = self.onboarding.start(sender_id)
            return TelegramReply(text=prompt, keyboard=options)

        if text.startswith("/help"):
            return TelegramReply(
                text="Nexus Befehle: /start /help /connect <plugin> /subagents /costs /facts"
            )

        if text.startswith("/connect"):
            plugin = text.replace("/connect", "", 1).strip() or "<plugin>"
            return TelegramReply(text=f"Plugin-Management: '{plugin}' wird verbunden.")

        if text.startswith("/subagents"):
            return TelegramReply(text="Sub-Agent Verwaltung: bald verfügbar.")

        if text.startswith("/costs"):
            return TelegramReply(text=f"Heutige Kosten: ${self.budget.get_daily_spend():.4f} ({self.budget.check_budget()})")

        if text.startswith("/facts"):
            return TelegramReply(text="Personal Facts CRUD: add/list/remove (coming soon).")

        state = self.onboarding.get_state(sender_id)
        if state and state.step == OnboardingStep.NAME and text:
            prompt, options = self.onboarding.handle_name(sender_id, text)
            return TelegramReply(text=prompt, keyboard=options)

        msg = self.channel.receive(payload)

        if msg.voice_audio:
            try:
                stt_text = self.voice.receive_voice(msg.voice_audio)
            except ValueError:
                return TelegramReply(text="Sprachnachricht konnte nicht verarbeitet werden. Bitte tippe deine Anfrage.")

            msg = msg.model_copy(update={"text": stt_text})
            response = self.coordinator.process(msg)
            tts = self.voice.synthesize_voice(response.text)
            return TelegramReply(text=response.text, voice=tts)

        if payload.get("callback_query"):
            data = str(payload["callback_query"].get("data", ""))
            return TelegramReply(text=f"Bestätigung erhalten: {data}")

        if state and state.step == OnboardingStep.PROVIDER and text:
            return TelegramReply(text=self.onboarding.handle_provider(sender_id, text))
        if state and state.step == OnboardingStep.LANGUAGE and text:
            return TelegramReply(text=self.onboarding.handle_language(sender_id, text))

        response = self.coordinator.process(msg)
        formatted = self.channel.format_response(response.text, tenant_name=msg.tenant_id)
        return TelegramReply(text=formatted)
