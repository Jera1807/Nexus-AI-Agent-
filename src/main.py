from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI

from src.agent.loop import AgentLoop
from src.channels.web import WebChannel
from src.config import settings
from src.db.models import ConversationEvent
from src.db.supabase import InMemorySupabaseClient

app = FastAPI(title="Nexus Agent", version="0.1.0")

_agent_loop = AgentLoop()
_web_channel = WebChannel()
_db = InMemorySupabaseClient()


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

    result = _agent_loop.process(
        {
            "request_id": str(uuid4()),
            "tenant_id": message.tenant_id,
            "sender_id": message.sender_id,
            "channel": message.channel,
            "text": message.text,
        }
    )

    return {
        "tenant_id": message.tenant_id,
        "response": _web_channel.format_response(result["text"], tenant_name=message.tenant_id),
        "intent": result["intent"],
    }


@app.get("/events")
async def list_events(tenant_id: str | None = None) -> dict:
    return {"items": _db.list_events(tenant_id=tenant_id)}
