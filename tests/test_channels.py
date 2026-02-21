from src.channels.base import build_disclosure
from src.channels.telegram import TelegramChannel
from src.channels.web import WebChannel


def test_web_message_parsing_and_response_format() -> None:
    channel = WebChannel()
    message = channel.receive(
        {
            "sender_id": "web-user-1",
            "tenant_id": "example_tenant",
            "text": "Hallo, wie sind die Öffnungszeiten?",
            "message_id": "m-1",
        }
    )

    assert message.channel == "web"
    assert message.sender_id == "web-user-1"
    assert message.tenant_id == "example_tenant"
    assert "Öffnungszeiten" in message.text

    response = channel.format_response("Wir sind Mo-Fr 9-18 Uhr da.", "Beauty & Nailschool Bochum")
    assert "KI-Assistent" in response
    assert "Beauty & Nailschool Bochum" in response


def test_telegram_message_parsing_uses_default_tenant() -> None:
    channel = TelegramChannel(default_tenant_id="tenant_from_config")
    message = channel.receive(
        {
            "message_id": 42,
            "from": {"id": 999},
            "chat": {"id": 12345},
            "text": "Ich möchte buchen",
        }
    )

    assert message.channel == "telegram"
    assert message.sender_id == "999"
    assert message.tenant_id == "tenant_from_config"


def test_disclosure_builder_contains_tenant_name() -> None:
    disclosure = build_disclosure("Beauty & Nailschool Bochum")
    assert "KI-Assistent" in disclosure
    assert "Beauty & Nailschool Bochum" in disclosure
