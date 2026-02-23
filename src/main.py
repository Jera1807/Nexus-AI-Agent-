from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from fastapi.concurrency import run_in_threadpool

from src.channels.telegram import TelegramBotService
from src.channels.web import WebChannel
from src.config import settings
from src.db.client import create_event_store
from src.db.models import ConversationEvent
from src.orchestration.coordinator import Coordinator

_coordinator: Coordinator | None = None
_web_channel = WebChannel()
_telegram_bot: TelegramBotService | None = None
_db = create_event_store(settings)
_telegram_task: asyncio.Task | None = None


async def _telegram_polling_stub() -> None:
    while True:
        await asyncio.sleep(60)


def _build_runtime_services() -> tuple[Coordinator, TelegramBotService]:
    coordinator = Coordinator()
    telegram_bot = TelegramBotService(coordinator=coordinator)
    return coordinator, telegram_bot


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _coordinator, _telegram_bot, _telegram_task
    _coordinator, _telegram_bot = _build_runtime_services()

    if settings.telegram_bot_token:
        _telegram_task = asyncio.create_task(_telegram_polling_stub())

    try:
        yield
    finally:
        if _telegram_task is not None:
            _telegram_task.cancel()
            with suppress(asyncio.CancelledError):
                await _telegram_task


app = FastAPI(title="Nexus Agent", version="0.1.0", lifespan=lifespan)


def _require_services() -> tuple[Coordinator, TelegramBotService]:
    if _coordinator is None or _telegram_bot is None:
        return _build_runtime_services()
    return _coordinator, _telegram_bot


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.post("/chat/web")
async def web_chat(payload: dict) -> dict:
    coordinator, _ = _require_services()
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

    result = await run_in_threadpool(coordinator.process, message)

    return {
        "tenant_id": message.tenant_id,
        "response": _web_channel.format_response(result.text, tenant_name=message.tenant_id),
        "intent": result.intent,
    }


@app.post("/chat/telegram")
async def telegram_chat(
    payload: dict,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict:
    _, telegram_bot = _require_services()

    if settings.telegram_webhook_secret:
        if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
            raise HTTPException(status_code=401, detail="invalid telegram webhook secret")

    reply = await run_in_threadpool(telegram_bot.handle_update, payload)
    return {"text": reply.text, "has_voice": reply.voice is not None, "keyboard": reply.keyboard}


@app.get("/events")
async def list_events(tenant_id: str | None = None) -> dict:
    return {"items": _db.list_events(tenant_id=tenant_id)}
