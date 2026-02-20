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


class RoutingDecision(BaseModel):
    intent: str
    tier: Tier
    risk_level: RiskLevel
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
