from backend.services.retrieval.vector_search import ChunkResult


def merge_results_rrf(vector_results: list[ChunkResult], keyword_results: list[ChunkResult], k: int = 60) -> list[ChunkResult]:
    scores: dict[str, float] = {}
    chunks: dict[str, ChunkResult] = {}

    for rank, chunk in enumerate(vector_results, start=1):
        scores[chunk.id] = scores.get(chunk.id, 0.0) + (1.0 / (k + rank))
        chunks[chunk.id] = chunk

    for rank, chunk in enumerate(keyword_results, start=1):
        scores[chunk.id] = scores.get(chunk.id, 0.0) + (1.0 / (k + rank))
        if chunk.id not in chunks:
            chunks[chunk.id] = chunk

    ranked_ids = sorted(scores, key=scores.get, reverse=True)
    return [chunks[chunk_id] for chunk_id in ranked_ids]
