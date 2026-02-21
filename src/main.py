from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from src.agent.loop import AgentLoop
from src.channels.web import WebChannel
from src.config import settings
from src.db.models import ConversationEvent
from src.db.supabase import InMemorySupabaseClient
from src.tenant.manager import TenantManager, TenantNotFoundError

app = FastAPI(title="Nexus Agent", version="0.1.0")

_tenant_manager = TenantManager(config_root=Path("configs"))
_agent_loop = AgentLoop()
_web_channel = WebChannel()
_db = InMemorySupabaseClient()


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.post("/chat/web")
async def web_chat(payload: dict) -> dict:
    message = _web_channel.receive(payload)

    # Resolve tenant context
    try:
        tenant_ctx = _tenant_manager.load_tenant_context(tenant_id=message.tenant_id)
    except TenantNotFoundError:
        raise HTTPException(status_code=404, detail=f"Tenant '{message.tenant_id}' not found")

    # Store incoming event
    _db.insert_event(
        ConversationEvent(
            event_id=str(uuid4()),
            tenant_id=message.tenant_id,
            sender_id=message.sender_id,
            channel=message.channel,
            text=message.text,
        )
    )

    # Run full agent pipeline
    response = _agent_loop.process(
        {
            "request_id": str(uuid4()),
            "tenant_id": message.tenant_id,
            "sender_id": message.sender_id,
            "channel": message.channel,
            "text": message.text,
        },
        tenant_context=tenant_ctx,
    )

    tenant_name = tenant_ctx.config.tenant.business_name
    return {
        "tenant_id": message.tenant_id,
        "response": _web_channel.format_response(response.text, tenant_name=tenant_name),
        "intent": response.intent,
        "confidence": response.confidence,
        "citations": [c.model_dump() for c in response.citations],
    }


@app.get("/events")
async def list_events(tenant_id: str | None = None) -> dict:
    return {"items": _db.list_events(tenant_id=tenant_id)}
