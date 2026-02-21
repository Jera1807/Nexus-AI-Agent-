from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable


@dataclass
class ProactiveJob:
    job_id: str
    tenant_id: str
    name: str
    run_at: datetime
    callback: Callable[[], None]


class JobRegistry:
    def __init__(self) -> None:
        self._jobs: dict[str, ProactiveJob] = {}

    def register(self, job: ProactiveJob) -> None:
        self._jobs[job.job_id] = job

    def due_jobs(self, now: datetime | None = None) -> list[ProactiveJob]:
        now = now or datetime.now(timezone.utc)
        return [job for job in self._jobs.values() if job.run_at <= now]

    def remove(self, job_id: str) -> None:
        self._jobs.pop(job_id, None)
