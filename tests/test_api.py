from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_web_chat_and_events_flow() -> None:
    chat_response = client.post(
        "/chat/web",
        json={
            "sender_id": "web-u1",
            "tenant_id": "example_tenant",
            "text": "Hallo, ich brauche Hilfe",
            "message_id": "m1",
        },
    )
    assert chat_response.status_code == 200
    body = chat_response.json()
    assert body["tenant_id"] == "example_tenant"
    assert body["intent"] == "general"

    events_response = client.get("/events", params={"tenant_id": "example_tenant"})
    assert events_response.status_code == 200
    items = events_response.json()["items"]
    assert len(items) >= 1
    assert items[-1]["sender_id"] == "web-u1"
