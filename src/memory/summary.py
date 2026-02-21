from __future__ import annotations

from src.memory.working import Turn


def summarize_turns(turns: list[Turn], max_chars: int = 400) -> str:
    """Build a compact rolling summary from recent turns."""
    if not turns:
        return ""

    lines: list[str] = []
    for turn in turns:
        content = " ".join(turn.content.split())
        lines.append(f"{turn.role}: {content}")

    summary = " | ".join(lines)
    if len(summary) <= max_chars:
        return summary

    return summary[: max_chars - 3].rstrip() + "..."
