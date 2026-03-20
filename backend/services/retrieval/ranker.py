from urllib.parse import urlparse

from backend.scoring.authority import compute_source_authority
from backend.services.retrieval.vector_search import ChunkResult


def score_chunk(chunk: ChunkResult, semantic_sim: float) -> float:
    domain = urlparse(chunk.source_url).netloc
    authority = compute_source_authority(domain=domain, source_type=chunk.source_type)
    return (
        0.40 * float(semantic_sim)
        + 0.25 * float(chunk.freshness_score)
        + 0.20 * float(chunk.trust_score)
        + 0.15 * float(authority)
    )


def rank_chunks(chunks: list[ChunkResult]) -> list[ChunkResult]:
    for chunk in chunks:
        chunk.final_score = score_chunk(chunk, chunk.similarity)
    return sorted(chunks, key=lambda item: item.final_score, reverse=True)
