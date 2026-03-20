BASE_SIGNAL_CONFIDENCE = {
    "funding": 0.85,
    "hiring": 0.75,
    "leadership_change": 0.80,
    "product_launch": 0.70,
    "website_change": 0.60,
    "expansion": 0.65,
    "layoff": 0.72,
    "acquisition": 0.88,
    "other": 0.50,
}


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def score_signal(signal: dict) -> float:
    """Compute a stable confidence score for a signal payload.

    Accepted optional inputs in signal payload:
    - signal_type: str
    - confidence: float [0, 1]
    - source_count: int
    - source_authority_avg: float [0, 1]
    - freshness_avg: float [0, 1]
    """
    signal_type = str(signal.get("signal_type") or "other")

    base = BASE_SIGNAL_CONFIDENCE.get(signal_type, BASE_SIGNAL_CONFIDENCE["other"])
    user_confidence = _clamp(float(signal.get("confidence", base)))
    source_count = max(int(signal.get("source_count", 1)), 0)
    source_authority_avg = _clamp(float(signal.get("source_authority_avg", 0.5)))
    freshness_avg = _clamp(float(signal.get("freshness_avg", 0.5)))

    source_boost = min(0.12, 0.04 * source_count)
    score = (
        0.35 * user_confidence
        + 0.25 * source_authority_avg
        + 0.20 * freshness_avg
        + 0.20 * _clamp(base + source_boost)
    )
    return _clamp(score)
