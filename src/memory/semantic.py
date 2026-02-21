from __future__ import annotations

import re
from dataclasses import dataclass

TOKEN_PATTERN = re.compile(r"\w+", flags=re.UNICODE)


@dataclass(frozen=True)
class SemanticSnippet:
    snippet_id: str
    text: str
    score: float


class SemanticMemoryIndex:
    """Very small lexical similarity index as pgvector placeholder."""

    def __init__(self) -> None:
        self._snippets: dict[str, str] = {}

    def upsert(self, snippet_id: str, text: str) -> None:
        self._snippets[snippet_id] = text

    def search(self, query: str, top_k: int = 3) -> list[SemanticSnippet]:
        query_tokens = self._tokens(query)
        if not query_tokens:
            return []

        results: list[SemanticSnippet] = []
        for snippet_id, text in self._snippets.items():
            snippet_tokens = self._tokens(text)
            if not snippet_tokens:
                continue
            overlap = len(query_tokens & snippet_tokens)
            if overlap <= 0:
                continue
            score = overlap / len(query_tokens | snippet_tokens)
            results.append(SemanticSnippet(snippet_id=snippet_id, text=text, score=score))

        return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]

    def _tokens(self, text: str) -> set[str]:
        return {token.lower() for token in TOKEN_PATTERN.findall(text)}
