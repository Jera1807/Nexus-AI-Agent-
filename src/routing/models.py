from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Tier(str, Enum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RoutingDecision(BaseModel):
    intent: str
    tier: Tier
    risk_level: RiskLevel
    confidence: float
    requires_confirmation: bool = False
    tools_to_load: list[str] = Field(default_factory=list)
    source: Literal["keyword", "semantic_router", "llm_classifier"] = "keyword"
    rationale: str = ""

    @field_validator("confidence")
    @classmethod
    def _clamp_confidence(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("confidence must be in [0.0, 1.0]")
        return v
