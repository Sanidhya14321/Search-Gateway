import math
from datetime import datetime, timezone


DECAY_RATES = {
    "news_article": 0.10,
    "job_board": 0.07,
    "company_website": 0.04,
    "linkedin": 0.03,
    "crunchbase": 0.03,
    "github": 0.02,
    "pdf_upload": 0.01,
    "unknown": 0.08,
}


def compute_freshness_score(fetched_at: datetime, decay_rate: float = 0.05) -> float:
    if fetched_at is None:
        return 0.1

    timestamp = fetched_at if fetched_at.tzinfo else fetched_at.replace(tzinfo=timezone.utc)
    days_old = max((datetime.now(timezone.utc) - timestamp).days, 0)
    return max(0.0, math.exp(-decay_rate * days_old))


def compute_freshness_for_source(fetched_at: datetime, source_type: str) -> float:
    rate = DECAY_RATES.get(source_type, 0.05)
    return compute_freshness_score(fetched_at=fetched_at, decay_rate=rate)
