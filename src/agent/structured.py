from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class AgentResponse:
    text: str
    intent: str
    confidence: float
    citations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
