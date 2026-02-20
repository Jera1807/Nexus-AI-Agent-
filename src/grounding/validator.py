from __future__ import annotations

from dataclasses import dataclass, field

from src.grounding.citations import citation_exists, extract_citations
from src.grounding.entity_registry import EntityRegistry


@dataclass
class GroundingResult:
    passed: bool
    violations: list[str] = field(default_factory=list)
    citations: list[str] = field(default_factory=list)


def validate_grounding(answer_text: str, registry: EntityRegistry, require_citations: bool = True) -> GroundingResult:
    citations = extract_citations(answer_text)
    violations: list[str] = []

    if require_citations and not citations:
        violations.append("missing_citation")

    for citation in citations:
        if not citation_exists(citation, registry.valid_citations):
            violations.append(f"invalid_citation:{citation}")

    return GroundingResult(
        passed=len(violations) == 0,
        violations=violations,
        citations=citations,
    )
