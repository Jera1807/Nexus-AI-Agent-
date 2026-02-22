from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentResponse(BaseModel):
    text: str
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
