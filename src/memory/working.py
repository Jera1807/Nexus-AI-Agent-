from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Turn:
    role: str
    content: str


class WorkingMemoryStore:
    """In-memory working memory abstraction (Redis replacement for local/dev tests)."""

    def __init__(self, max_turns: int = 12) -> None:
        self.max_turns = max_turns
        self._store: dict[str, deque[Turn]] = defaultdict(lambda: deque(maxlen=self.max_turns))

    def append(self, session_id: str, role: str, content: str) -> None:
        self._store[session_id].append(Turn(role=role, content=content))

    def get(self, session_id: str) -> list[Turn]:
        return list(self._store[session_id])

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
