from __future__ import annotations

from src.grounding.entity_registry import EntityRegistry
from src.grounding.validator import GroundingResult, validate_grounding


FAIL_SAFE_MESSAGE = "Kann ich nicht zuverlässig beantworten."


def repair_or_fallback(answer_text: str, registry: EntityRegistry, max_retries: int = 1) -> tuple[str, GroundingResult]:
    result = validate_grounding(answer_text, registry=registry)
    if result.passed:
        return answer_text, result

    if max_retries <= 0:
        return FAIL_SAFE_MESSAGE, result

    candidate_ids = list(registry.valid_citations)
    for citation_id in candidate_ids[:max_retries]:
        repaired = f"{answer_text.rstrip()} [{citation_id}]"
        repaired_result = validate_grounding(repaired, registry=registry)
        if repaired_result.passed:
            return repaired, repaired_result
        result = repaired_result

    return FAIL_SAFE_MESSAGE, result
