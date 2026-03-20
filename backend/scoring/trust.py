import math


BASE_TRUST = {
    "news_article": 0.80,
    "linkedin": 0.82,
    "crunchbase": 0.85,
    "company_website": 0.75,
    "github": 0.78,
    "job_board": 0.65,
    "blog_post": 0.55,
    "pdf_upload": 0.70,
    "twitter": 0.50,
    "unknown": 0.30,
}


def compute_trust_score(source_type: str, cross_ref_count: int = 0, is_verified: bool = False) -> float:
    base = BASE_TRUST.get(source_type, 0.30)
    base += min(0.15, 0.05 * math.log1p(cross_ref_count))
    if is_verified:
        base += 0.08
    return min(base, 1.0)
