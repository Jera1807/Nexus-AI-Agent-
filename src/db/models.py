from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ConversationEvent:
    event_id: str
    tenant_id: str
    sender_id: str
    channel: str
    text: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
