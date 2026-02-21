from __future__ import annotations

from datetime import date, timedelta


def get_mock_availability(start_date: date | None = None, days: int = 5) -> list[dict[str, str]]:
    start = start_date or date.today()
    out: list[dict[str, str]] = []
    for i in range(days):
        d = start + timedelta(days=i)
        out.append({"date": d.isoformat(), "timeslot": "10:00"})
        out.append({"date": d.isoformat(), "timeslot": "14:00"})
    return out
