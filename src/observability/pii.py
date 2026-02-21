from __future__ import annotations

import re
from dataclasses import dataclass

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s\-/]{6,}\d)")


@dataclass
class PiiRedactionResult:
    text: str
    replacements: dict[str, str]


def redact_pii(text: str) -> PiiRedactionResult:
    replacements: dict[str, str] = {}

    def _replace_email(match: re.Match[str]) -> str:
        src = match.group(0)
        token = f"[EMAIL_{len(replacements)+1}]"
        replacements[src] = token
        return token

    redacted = EMAIL_RE.sub(_replace_email, text)

    def _replace_phone(match: re.Match[str]) -> str:
        src = match.group(0)
        token = f"[PHONE_{len(replacements)+1}]"
        replacements[src] = token
        return token

    redacted = PHONE_RE.sub(_replace_phone, redacted)
    return PiiRedactionResult(text=redacted, replacements=replacements)
