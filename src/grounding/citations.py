from __future__ import annotations

import re

CITATION_PATTERN = re.compile(r"\[(KB-[A-Z0-9_]+-[A-Z0-9_-]+)\]")


def extract_citations(text: str) -> list[str]:
    return CITATION_PATTERN.findall(text)


def citation_exists(citation_id: str, known_ids: set[str]) -> bool:
    return citation_id in known_ids
