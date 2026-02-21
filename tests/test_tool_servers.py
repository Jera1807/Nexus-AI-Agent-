from datetime import date
from pathlib import Path

from src.tools.servers.calendar import get_mock_availability
from src.tools.servers.customer import CustomerProfile, CustomerStore
from src.tools.servers.knowledge_base import kb_search, load_kb_entries


def test_kb_search_returns_relevant_entry() -> None:
    entries = load_kb_entries(Path("configs/tenants/example_tenant/kb_seed.yaml"))
    results = kb_search("Öffnungszeiten", entries, top_k=1)
    assert len(results) == 1
    assert "Öffnungszeiten" in results[0]["title"]


def test_calendar_mock_availability_shape() -> None:
    slots = get_mock_availability(start_date=date(2026, 1, 1), days=2)
    assert len(slots) == 4
    assert slots[0]["date"] == "2026-01-01"


def test_customer_store_upsert_and_get() -> None:
    store = CustomerStore()
    store.upsert(CustomerProfile(customer_id="c1", first_name="Max", last_name="Mustermann", email="max@example.com"))
    profile = store.get("c1")
    assert profile is not None
    assert profile["first_name"] == "Max"
