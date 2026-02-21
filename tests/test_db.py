from src.db.models import ConversationEvent
from src.db.supabase import InMemorySupabaseClient


def test_insert_and_filter_events() -> None:
    client = InMemorySupabaseClient()
    client.insert_event(ConversationEvent(event_id="e1", tenant_id="t1", sender_id="u1", channel="web", text="Hallo"))
    client.insert_event(ConversationEvent(event_id="e2", tenant_id="t2", sender_id="u2", channel="telegram", text="Hi"))

    t1_events = client.list_events(tenant_id="t1")
    assert len(t1_events) == 1
    assert t1_events[0]["event_id"] == "e1"
