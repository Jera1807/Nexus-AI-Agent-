from __future__ import annotations


def clamp_confidence(score: float) -> float:
    """Clamp confidence scores to [0.0, 1.0]."""
    return max(0.0, min(1.0, score))


def combine_confidence(*scores: float, weights: list[float] | None = None) -> float:
    """Combine one or more confidence scores via weighted average.

    If weights are not given, all scores are weighted equally.
    """
    if not scores:
        return 0.0

    if weights is None:
        weights = [1.0] * len(scores)

    if len(weights) != len(scores):
        raise ValueError("weights length must match scores length")

    weighted_sum = sum(clamp_confidence(score) * weight for score, weight in zip(scores, weights))
    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("sum(weights) must be > 0")

    return clamp_confidence(weighted_sum / total_weight)


def confidence_label(score: float) -> str:
    normalized = clamp_confidence(score)
    if normalized >= 0.8:
        return "high"
    if normalized >= 0.5:
        return "medium"
    return "low"
