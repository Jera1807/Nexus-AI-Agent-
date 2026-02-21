from __future__ import annotations

from dataclasses import dataclass

from src.memory.semantic import SemanticSnippet
from src.memory.working import Turn


@dataclass
class ContextPackage:
    working_turns: list[Turn]
    summary: str
    semantic_snippets: list[SemanticSnippet]


def build_context_package(
    working_turns: list[Turn],
    summary: str,
    semantic_snippets: list[SemanticSnippet],
    max_chars: int = 2500,
    prefer_semantic: bool = False,
) -> ContextPackage:
    """Return context trimmed to a rough character budget.

    Default prioritization keeps more recent turns first, then trims semantic snippets.
    Set `prefer_semantic=True` to trim turns more aggressively before removing snippets.
    """
    packaged_turns = working_turns
    packaged_summary = summary
    packaged_snippets = semantic_snippets

    def _size() -> int:
        turns_size = sum(len(t.content) + len(t.role) for t in packaged_turns)
        snippets_size = sum(len(s.text) for s in packaged_snippets)
        return turns_size + len(packaged_summary) + snippets_size

    if prefer_semantic:
        while packaged_turns and _size() > max_chars:
            packaged_turns = packaged_turns[1:]
        while packaged_snippets and _size() > max_chars:
            packaged_snippets = packaged_snippets[:-1]
    else:
        while packaged_snippets and _size() > max_chars:
            packaged_snippets = packaged_snippets[:-1]
        while packaged_turns and _size() > max_chars:
            packaged_turns = packaged_turns[1:]

    if _size() > max_chars:
        packaged_summary = packaged_summary[: max(0, max_chars // 3)]

    return ContextPackage(
        working_turns=packaged_turns,
        summary=packaged_summary,
        semantic_snippets=packaged_snippets,
    )
