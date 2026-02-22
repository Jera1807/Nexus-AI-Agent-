from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class InterAgentMessage(BaseModel):
    task_id: str
    from_agent: str
    to_agent: str
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))


class TaskRequest(InterAgentMessage):
    pass


class TaskResult(InterAgentMessage):
    success: bool = True


class SecurityReview(InterAgentMessage):
    pass


class BudgetQuery(InterAgentMessage):
    pass


class BudgetResponse(InterAgentMessage):
    pass
