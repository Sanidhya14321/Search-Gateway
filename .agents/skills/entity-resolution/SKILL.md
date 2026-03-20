---
name: entity-resolution
description: >
  Resolve a company name, person name, email domain, or account ID to a canonical
  entity record in the CRMind database. Use this skill when implementing fuzzy
  matching, deduplication, canonical ID assignment, alias handling, or any code
  that maps a raw input string to a structured entity. Keywords: entity resolution,
  canonical ID, company lookup, person lookup, fuzzy match, dedup, alias, domain match.
---

## Purpose

Entity resolution is the process of taking a raw, potentially ambiguous input (e.g.
"Acme Corp", "acme.com", "John Doe @ Acme") and mapping it to a single canonical
record in the `companies`, `people`, or `accounts` table.

---

## Canonical ID Format

- Companies: `comp_{slugified_name}` e.g. `comp_acme_corp`
- People: `per_{first}_{last}_{company_slug}` e.g. `per_john_doe_acme`
- Accounts: `acc_{uuid_short}` e.g. `acc_ab12cd34`

---

## Resolution Algorithm

### Step 1 — Exact match
```python
# Try exact domain match first (most reliable for companies)
result = db.query(
    "SELECT * FROM companies WHERE domain = $1 LIMIT 1",
    [normalize_domain(input_domain)]
)
```

### Step 2 — Fuzzy name match (pg_trgm)
```python
result = db.query("""
    SELECT *, similarity(canonical_name, $1) AS sim
    FROM companies
    WHERE similarity(canonical_name, $1) > 0.4
    ORDER BY sim DESC
    LIMIT 5
""", [input_name])
```

### Step 3 — Alias match
```python
result = db.query(
    "SELECT * FROM companies WHERE $1 = ANY(aliases)",
    [input_name.lower()]
)
```

### Step 4 — Embedding similarity (fallback)
```python
# Only used when steps 1-3 return nothing
query_embedding = embed(input_name)
result = db.query("""
    SELECT c.*, (embedding <=> $1::vector) AS dist
    FROM company_embeddings e
    JOIN companies c ON c.id = e.company_id
    ORDER BY dist ASC
    LIMIT 3
""", [query_embedding])
```

### Step 5 — Confidence scoring
```python
def score_match(candidate, input_str, match_type):
    base = {"exact_domain": 0.98, "exact_name": 0.95, "fuzzy": 0.7, "alias": 0.88, "embedding": 0.55}
    score = base[match_type]
    # Boost if industry / location context matches
    return min(score, 1.0)
```

---

## Response Shape

```python
@dataclass
class ResolvedEntity:
    canonical_id: str
    entity_type: str           # "company" | "person" | "account"
    canonical_name: str
    confidence: float          # 0.0 – 1.0
    match_type: str            # "exact_domain" | "fuzzy" | "alias" | "embedding"
    record: dict               # full DB row
    alternatives: List[dict]   # other candidates with scores
```

---

## Rules

- **Never create a new entity silently.** If confidence < 0.6, return unresolved and flag.
- **Always check aliases array** before creating a duplicate company record.
- **Domain normalization:** strip `www.`, lowercase, strip trailing slash.
- **Person disambiguation:** require at least company context OR email hint to resolve a person
  confidently when multiple people share the same name.
- **Deduplication trigger:** if two records share domain AND similarity > 0.9, merge them.

---

## File locations in this project

```
backend/
  services/
    entity_resolver.py     ← main resolution logic
    entity_merger.py       ← dedup and merge
  models/
    resolved_entity.py     ← dataclass above
  tests/
    test_entity_resolver.py
```

---

## Common pitfalls

- `"Apple"` matches many things — always require domain or context
- Names with legal suffixes ("Inc", "LLC", "Ltd") must be stripped before matching
- Person names: "John Smith" is extremely common — always require company context
- Domains with country TLDs: `acme.co.uk` → normalize to `acme` as slug