from __future__ import annotations

import asyncio
from contextlib import suppress
from uuid import uuid4

from fastapi import FastAPI

from src.channels.telegram import TelegramBotService
from src.channels.web import WebChannel
from src.config import settings
from src.db.client import create_event_store
from src.db.models import ConversationEvent
from src.orchestration.coordinator import Coordinator

app = FastAPI(title="Nexus Agent", version="0.1.0")

_coordinator = Coordinator()
_web_channel = WebChannel()
_telegram_bot = TelegramBotService(coordinator=_coordinator)
_db = create_event_store(settings)
_telegram_task: asyncio.Task | None = None


async def _telegram_polling_stub() -> None:
    while True:
        await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event() -> None:
    global _telegram_task
    if settings.telegram_bot_token:
        _telegram_task = asyncio.create_task(_telegram_polling_stub())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if _telegram_task is not None:
        _telegram_task.cancel()
        with suppress(asyncio.CancelledError):
            await _telegram_task


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.post("/chat/web")
async def web_chat(payload: dict) -> dict:
    message = _web_channel.receive(payload)

    _db.insert_event(
        ConversationEvent(
            event_id=str(uuid4()),
            tenant_id=message.tenant_id,
            sender_id=message.sender_id,
            channel=message.channel,
            text=message.text,
        )
    )

    result = _coordinator.process(message)

    return {
        "tenant_id": message.tenant_id,
        "response": _web_channel.format_response(result.text, tenant_name=message.tenant_id),
        "intent": result.intent,
    }


@app.post("/chat/telegram")
async def telegram_chat(payload: dict) -> dict:
    reply = _telegram_bot.handle_update(payload)
    return {"text": reply.text, "has_voice": reply.voice is not None, "keyboard": reply.keyboard}


@app.get("/events")
async def list_events(tenant_id: str | None = None) -> dict:
    return {"items": _db.list_events(tenant_id=tenant_id)}
