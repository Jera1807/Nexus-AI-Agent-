from datetime import datetime, timedelta, timezone

from src.proactive.consent import ConsentStore
from src.proactive.jobs import JobRegistry, ProactiveJob
from src.proactive.scheduler import ProactiveScheduler


def test_scheduler_executes_due_jobs_for_opted_in_user() -> None:
    calls: list[str] = []
    registry = JobRegistry()
    consent = ConsentStore()
    consent.set_consent("tenant-a", "campaign-1", opted_in=True, frequency_cap_per_day=1)

    registry.register(
        ProactiveJob(
            job_id="j1",
            tenant_id="tenant-a",
            name="campaign-1",
            run_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            callback=lambda: calls.append("j1"),
        )
    )

    scheduler = ProactiveScheduler(registry, consent)
    result = scheduler.run_once()

    assert result.executed == ["j1"]
    assert calls == ["j1"]


def test_scheduler_skips_without_consent() -> None:
    calls: list[str] = []
    registry = JobRegistry()
    consent = ConsentStore()

    registry.register(
        ProactiveJob(
            job_id="j2",
            tenant_id="tenant-a",
            name="campaign-2",
            run_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            callback=lambda: calls.append("j2"),
        )
    )

    scheduler = ProactiveScheduler(registry, consent)
    result = scheduler.run_once()

    assert result.executed == []
    assert result.skipped == ["j2"]
    assert calls == []


def test_scheduler_respects_frequency_cap() -> None:
    calls: list[str] = []
    registry = JobRegistry()
    consent = ConsentStore()
    consent.set_consent("tenant-a", "campaign-3", opted_in=True, frequency_cap_per_day=1)

    now = datetime.now(timezone.utc)
    registry.register(ProactiveJob("j3", "tenant-a", "campaign-3", now - timedelta(minutes=2), lambda: calls.append("j3")))
    registry.register(ProactiveJob("j4", "tenant-a", "campaign-3", now - timedelta(minutes=1), lambda: calls.append("j4")))

    scheduler = ProactiveScheduler(registry, consent)
    result = scheduler.run_once(now=now)

    assert result.executed == ["j3"]
    assert "j4" in result.skipped
    assert calls == ["j3"]
