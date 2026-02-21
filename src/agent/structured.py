from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Citation(BaseModel):
    id: str
    fact: str
    source: str = ""


class UIComponent(BaseModel):
    type: str = "text"
    data: dict[str, Any] = Field(default_factory=dict)


class Turn(BaseModel):
    role: str
    content: str


class Chunk(BaseModel):
    chunk_id: str
    text: str
    score: float = 0.0
    source_id: str = ""


class DecisionLog(BaseModel):
    request_id: str = ""
    tenant_id: str = ""
    channel: str = "web"
    sender_id: str = ""
    input_text: str = ""
    predicted_intent: str = "fallback"
    tier: str = "tier_2"
    risk_level: str = "medium"
    confidence: float = 0.0
    source: str = "keyword"
    tools_considered: list[str] = Field(default_factory=list)
    tools_called: list[str] = Field(default_factory=list)
    grounding_passed: bool = False
    citations: list[str] = Field(default_factory=list)
    response_text: str = ""
    latency_ms: int = 0
    token_in: int = 0
    token_out: int = 0


class ContextBundle(BaseModel):
    last_turns: list[Turn] = Field(default_factory=list)
    summary: str = ""
    rag_snippets: list[Chunk] = Field(default_factory=list)
    total_tokens: int = 0


class AgentResponse(BaseModel):
    text: str
    citations: list[Citation] = Field(default_factory=list)
    ui_component: UIComponent | None = None
    fallback_text: str = ""
    confidence: float = 0.0
    intent: str = "fallback"
    decision_log: DecisionLog = Field(default_factory=DecisionLog)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
