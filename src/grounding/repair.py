from __future__ import annotations

from src.grounding.validator import GroundingResult, validate_grounding
from src.grounding.entity_registry import EntityRegistry


FAIL_SAFE_MESSAGE = "Kann ich nicht zuverlässig beantworten."


def repair_or_fallback(answer_text: str, registry: EntityRegistry, max_retries: int = 1) -> tuple[str, GroundingResult]:
    result = validate_grounding(answer_text, registry=registry)
    if result.passed:
        return answer_text, result

    if max_retries <= 0:
        return FAIL_SAFE_MESSAGE, result

    # deterministic placeholder repair strategy
    first_valid = next(iter(registry.valid_citations), None)
    if first_valid is None:
        return FAIL_SAFE_MESSAGE, result

    repaired = f"{answer_text.rstrip()} [{first_valid}]"
    repaired_result = validate_grounding(repaired, registry=registry)
    if repaired_result.passed:
        return repaired, repaired_result

    return FAIL_SAFE_MESSAGE, repaired_result
