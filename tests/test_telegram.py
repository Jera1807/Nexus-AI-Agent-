import base64

from src.channels.telegram import TelegramBotService


def _payload(text: str = "", sender: str = "u1") -> dict:
    return {
        "from": {"id": sender},
        "chat": {"id": 123},
        "message_id": "m1",
        "text": text,
        "tenant_id": "example_tenant",
    }


def test_start_triggers_onboarding() -> None:
    bot = TelegramBotService()
    reply = bot.handle_update(_payload("/start"))
    assert "Provider" in reply.text or "Provider" in reply.text.replace("ä", "a")
    assert reply.keyboard


def test_text_message_gets_agent_response() -> None:
    bot = TelegramBotService()
    reply = bot.handle_update(_payload("hello"))
    assert "Hinweis" in reply.text


def test_voice_message_stt_response_tts() -> None:
    bot = TelegramBotService()
    audio_b64 = base64.b64encode(b"voice-bytes").decode("utf-8")
    payload = _payload("")
    payload["voice"] = {"audio_base64": audio_b64}

    reply = bot.handle_update(payload)
    assert reply.voice is not None
    assert isinstance(reply.voice, bytes)


def test_inline_keyboard_confirmation_callback() -> None:
    bot = TelegramBotService()
    payload = _payload("")
    payload["callback_query"] = {"data": "confirm:task-1"}
    reply = bot.handle_update(payload)
    assert "Bestätigung" in reply.text


def test_connect_shows_plugin_list() -> None:
    bot = TelegramBotService()
    reply = bot.handle_update(_payload("/connect gmail"))
    assert "gmail" in reply.text
