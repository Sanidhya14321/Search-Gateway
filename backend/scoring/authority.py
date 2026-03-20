HIGH_AUTHORITY_DOMAINS = {
    "techcrunch.com": 0.95,
    "crunchbase.com": 0.92,
    "linkedin.com": 0.90,
    "reuters.com": 0.93,
    "bloomberg.com": 0.94,
    "github.com": 0.88,
    "sec.gov": 0.98,
    "businesswire.com": 0.85,
    "prnewswire.com": 0.82,
}

SOURCE_TYPE_AUTHORITY = {
    "news_article": 0.80,
    "linkedin": 0.85,
    "crunchbase": 0.88,
    "company_website": 0.75,
    "github": 0.78,
    "job_board": 0.60,
    "blog_post": 0.50,
    "unknown": 0.25,
}


def compute_source_authority(domain: str, source_type: str) -> float:
    if domain in HIGH_AUTHORITY_DOMAINS:
        return HIGH_AUTHORITY_DOMAINS[domain]
    return SOURCE_TYPE_AUTHORITY.get(source_type, 0.25)
