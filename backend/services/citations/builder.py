from urllib.parse import urlparse


def extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return ""


def build_citation(chunk: dict) -> dict:
    text = str(chunk.get("chunk_text", "")).strip()
    excerpt = text[:200] + ("..." if len(text) > 200 else "")
    return {
        "source_id": str(chunk.get("id", "")),
        "url": str(chunk.get("source_url", "")),
        "source_type": str(chunk.get("source_type", "unknown")),
        "domain": extract_domain(str(chunk.get("source_url", ""))),
        "title": chunk.get("title"),
        "fetched_at": chunk.get("fetched_at"),
        "trust_score": float(chunk.get("trust_score", 0.5)),
        "freshness_score": float(chunk.get("freshness_score", 0.5)),
        "excerpt": excerpt,
        "relevance_score": float(chunk.get("final_score", chunk.get("similarity", 0.0))),
    }
