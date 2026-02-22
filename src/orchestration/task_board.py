from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


VALID_STATUSES = {"pending", "running", "completed", "failed", "vetoed"}


@dataclass
class TaskRecord:
    task_id: str
    request_id: str
    status: str = "pending"
    payload: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


class TaskBoard:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskRecord] = {}
        self._by_request: dict[str, list[str]] = defaultdict(list)

    def create_task(self, task_id: str, request_id: str, payload: dict | None = None) -> TaskRecord:
        record = TaskRecord(task_id=task_id, request_id=request_id, payload=payload or {})
        self._tasks[task_id] = record
        self._by_request[request_id].append(task_id)
        return record

    def update_status(self, task_id: str, status: str) -> TaskRecord:
        if status not in VALID_STATUSES:
            raise ValueError(f"invalid status '{status}'")
        task = self._tasks[task_id]
        task.status = status
        return task

    def get_task(self, task_id: str) -> TaskRecord | None:
        return self._tasks.get(task_id)

    def list_tasks_for_request(self, request_id: str) -> list[TaskRecord]:
        return [self._tasks[task_id] for task_id in self._by_request.get(request_id, [])]
