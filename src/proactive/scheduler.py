from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.proactive.consent import ConsentStore
from src.proactive.jobs import JobRegistry


@dataclass
class SchedulerResult:
    executed: list[str]
    skipped: list[str]


class ProactiveScheduler:
    def __init__(self, registry: JobRegistry, consent_store: ConsentStore) -> None:
        self.registry = registry
        self.consent_store = consent_store
        self._sent_today: dict[tuple[str, str, str], int] = {}

    def run_once(self, now: datetime | None = None) -> SchedulerResult:
        now = now or datetime.now(timezone.utc)
        executed: list[str] = []
        skipped: list[str] = []

        for job in self.registry.due_jobs(now=now):
            consent = self.consent_store.get_consent(job.tenant_id, job.name)
            key = (job.tenant_id, job.name, now.date().isoformat())
            sent_count = self._sent_today.get(key, 0)

            if not consent.opted_in:
                skipped.append(job.job_id)
                continue

            if sent_count >= consent.frequency_cap_per_day:
                skipped.append(job.job_id)
                continue

            job.callback()
            self._sent_today[key] = sent_count + 1
            executed.append(job.job_id)
            self.registry.remove(job.job_id)

        return SchedulerResult(executed=executed, skipped=skipped)
