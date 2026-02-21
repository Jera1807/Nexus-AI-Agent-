from src.channels.whatsapp import WhatsAppChannel


def test_whatsapp_channel_parsing_and_response() -> None:
    ch = WhatsAppChannel(default_tenant_id="tenant_x")
    msg = ch.receive({"from": "49123", "text": "Hallo", "id": "w1"})

    assert msg.channel == "whatsapp"
    assert msg.tenant_id == "tenant_x"
    assert msg.sender_id == "49123"

    out = ch.format_response("Antwort", "Beauty & Nailschool Bochum")
    assert "KI-Assistent" in out
