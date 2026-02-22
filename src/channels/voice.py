from __future__ import annotations


class VoicePipeline:
    def __init__(self, whisper_model: str = "base") -> None:
        self.whisper_model = whisper_model

    def receive_voice(self, audio_bytes: bytes) -> str:
        if not audio_bytes:
            raise ValueError("empty audio")
        # Placeholder STT implementation (session-2 baseline).
        return "Transcribed voice message"

    def synthesize_voice(self, text: str) -> bytes:
        if not text.strip():
            raise ValueError("empty text")
        # Placeholder TTS implementation (session-2 baseline).
        return f"VOICE:{text}".encode("utf-8")
