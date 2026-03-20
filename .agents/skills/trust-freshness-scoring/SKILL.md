---
name: trust-freshness-scoring
description: >
  Implement trust scoring, freshness scoring, and source authority ranking for
  CRMind. Use this skill when computing scores for retrieved chunks, source documents,
  entities, or signals. Covers exponential decay freshness, source type authority
  weights, cross-reference boosting, and score persistence. Keywords: trust score,
  freshness score, source authority, scoring, ranking, exponential decay, reliability,
  evidence quality, signal confidence.
---

## Scoring Model Overview

```
final_score = (
  0.40 × semantic_similarity      ← how relevant is the chunk to the query
  + 0.25 × freshness_score        ← how recently was this source fetched
  + 0.20 × trust_score            ← how reliable is this source
  + 0.15 × source_authority       ← domain-level authority weight
)
```

---

## Freshness Score

Exponential decay from fetch date. Score = 1.0 when just fetched, decays toward 0.

```python
import math
from datetime import datetime, timezone

def compute_freshness_score(
    fetched_at: datetime,
    decay_rate: float = 0.05,   # tune this per source type
) -> float:
    """
    decay_rate=0.05 → half-life ≈ 14 days
    decay_rate=0.03 → half-life ≈ 23 days (for slower-changing sources)
    decay_rate=0.10 → half-life ≈ 7 days (for news)
    """
    if fetched_at is None:
        return 0.1   # unknown freshness → pessimistic
    days_old = (datetime.now(timezone.utc) - fetched_at.replace(tzinfo=timezone.utc)).days
    return max(0.0, math.exp(-decay_rate * days_old))


# Source-type specific decay rates
DECAY_RATES = {
    "news_article":     0.10,   # goes stale fast
    "job_board":        0.07,
    "company_website":  0.04,
    "linkedin":         0.03,
    "crunchbase":       0.03,
    "github":           0.02,
    "pdf_upload":       0.01,
    "unknown":          0.08,
}

def compute_freshness_for_source(fetched_at: datetime, source_type: str) -> float:
    rate = DECAY_RATES.get(source_type, 0.05)
    return compute_freshness_score(fetched_at, decay_rate=rate)
```

---

## Trust Score

Trust score reflects the inherent reliability of a source type and is boosted
by cross-referencing (the same fact appears in multiple independent sources).

```python
BASE_TRUST = {
    "news_article":     0.80,
    "linkedin":         0.82,
    "crunchbase":       0.85,
    "company_website":  0.75,
    "github":           0.78,
    "job_board":        0.65,
    "blog_post":        0.55,
    "pdf_upload":       0.70,
    "twitter":          0.50,
    "unknown":          0.30,
}

def compute_trust_score(
    source_type: str,
    cross_reference_count: int = 0,   # how many other sources confirm same fact
    is_verified: bool = False,
) -> float:
    base = BASE_TRUST.get(source_type, 0.30)

    # Boost for cross-references (logarithmic)
    cross_ref_boost = min(0.15, 0.05 * math.log1p(cross_reference_count))

    # Boost if entity is verified by human/admin
    verified_boost = 0.08 if is_verified else 0.0

    return min(1.0, base + cross_ref_boost + verified_boost)
```

---

## Source Authority Score

Domain-level authority based on source type and known high-authority domains.

```python
HIGH_AUTHORITY_DOMAINS = {
    "techcrunch.com":     0.95,
    "crunchbase.com":     0.92,
    "linkedin.com":       0.90,
    "reuters.com":        0.93,
    "bloomberg.com":      0.94,
    "github.com":         0.88,
    "sec.gov":            0.98,
    "businesswire.com":   0.85,
    "prnewswire.com":     0.82,
}

SOURCE_TYPE_AUTHORITY = {
    "news_article":     0.80,
    "linkedin":         0.85,
    "crunchbase":       0.88,
    "company_website":  0.75,
    "github":           0.78,
    "job_board":        0.60,
    "blog_post":        0.50,
    "unknown":          0.25,
}

def compute_source_authority(domain: str, source_type: str) -> float:
    if domain in HIGH_AUTHORITY_DOMAINS:
        return HIGH_AUTHORITY_DOMAINS[domain]
    return SOURCE_TYPE_AUTHORITY.get(source_type, 0.25)
```

---

## Signal Confidence Score

Signals (hiring, funding, etc.) have their own confidence calculation.

```python
def compute_signal_confidence(
    signal_type: str,
    source_count: int,        # how many sources mention this signal
    source_authority_avg: float,
    freshness_avg: float,
) -> float:
    """
    Higher confidence when:
    - multiple independent sources confirm it
    - sources are authoritative
    - sources are fresh
    """
    BASE_SIGNAL_CONFIDENCE = {
        "funding":           0.85,   # usually well-documented
        "hiring":            0.75,
        "leadership_change": 0.80,
        "product_launch":    0.70,
        "website_change":    0.60,
        "expansion":         0.65,
        "layoff":            0.72,
        "acquisition":       0.88,
        "other":             0.50,
    }

    base = BASE_SIGNAL_CONFIDENCE.get(signal_type, 0.50)
    source_boost = min(0.12, 0.04 * source_count)   # capped boost from multiple sources

    return min(1.0, (
        0.4 * base
        + 0.3 * source_authority_avg
        + 0.2 * freshness_avg
        + 0.1 * (base + source_boost)
    ))
```

---

## Updating Scores in Database

```python
async def refresh_entity_scores(entity_id: str, entity_type: str, db) -> None:
    """
    Recalculate and update freshness_score and trust_score for an entity.
    Run this after ingestion or on a schedule.
    """
    # Get all source docs for this entity
    sources = await db.fetch("""
        SELECT source_type, fetched_at, trust_score
        FROM source_documents
        WHERE entity_id = $1 AND entity_type = $2
        ORDER BY fetched_at DESC
        LIMIT 20
    """, entity_id, entity_type)

    if not sources:
        return

    # Average freshness of top sources
    freshness_scores = [
        compute_freshness_for_source(s["fetched_at"], s["source_type"])
        for s in sources
    ]
    avg_freshness = sum(freshness_scores) / len(freshness_scores)
    # Weight more recent sources heavier
    weighted_freshness = freshness_scores[0] * 0.5 + avg_freshness * 0.5

    # Average trust
    trust_scores = [compute_trust_score(s["source_type"]) for s in sources]
    avg_trust = sum(trust_scores) / len(trust_scores)

    table = "companies" if entity_type == "company" else "people"
    await db.execute(f"""
        UPDATE {table}
        SET freshness_score = $1, trust_score = $2, updated_at = NOW()
        WHERE id = $3
    """, weighted_freshness, avg_trust, entity_id)
```

---

## Scheduled Batch Score Refresh

```python
# Run via GitHub Actions CRON or ARQ worker

async def batch_refresh_stale_scores(db, threshold_days: int = 7):
    """Refresh scores for all entities not updated in threshold_days."""
    stale = await db.fetch("""
        SELECT id, 'company' as type FROM companies
        WHERE updated_at < NOW() - INTERVAL '$1 days'
        UNION ALL
        SELECT id, 'person' FROM people
        WHERE updated_at < NOW() - INTERVAL '$1 days'
    """, threshold_days)

    for entity in stale:
        await refresh_entity_scores(str(entity["id"]), entity["type"], db)
```

---

## File locations

```
backend/
  scoring/
    freshness.py          ← compute_freshness_score, DECAY_RATES
    trust.py              ← compute_trust_score, BASE_TRUST
    authority.py          ← compute_source_authority
    signals.py            ← compute_signal_confidence
    batch_refresh.py      ← batch_refresh_stale_scores
  tests/
    test_scoring.py
```