from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"\w+", flags=re.UNICODE)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(text)}


def load_kb_entries(path: Path) -> list[dict[str, Any]]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw or "{}")
    return data.get("entries", [])


def kb_search(query: str, kb_entries: list[dict[str, Any]], top_k: int = 3) -> list[dict[str, Any]]:
    q = _tokens(query)
    if not q:
        return []

    scored: list[tuple[float, dict[str, Any]]] = []
    for item in kb_entries:
        hay = f"{item.get('title','')} {item.get('snippet','')}"
        t = _tokens(hay)
        if not t:
            continue
        overlap = len(q & t)
        if overlap <= 0:
            continue
        score = overlap / len(q | t)
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]
