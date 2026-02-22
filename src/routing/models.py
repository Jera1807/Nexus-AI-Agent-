from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Tier(str, Enum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GroundingMode(str, Enum):
    STRICT = "strict"
    HYBRID = "hybrid"
    OPEN = "open"


class RoutingDecision(BaseModel):
    intent: str
    tier: Tier
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    grounding_mode: GroundingMode = GroundingMode.OPEN
    plugins_to_load: list[str] = Field(default_factory=list)
    should_delegate: bool = False
    requires_confirmation: bool = False
    tools_to_load: list[str] = Field(default_factory=list)
