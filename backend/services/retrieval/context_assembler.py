from backend.services.retrieval.vector_search import ChunkResult


def assemble_context(chunks: list[ChunkResult], max_tokens: int = 3000) -> str:
    context_parts: list[str] = []
    token_count = 0

    for chunk in chunks:
        fetched = chunk.fetched_at.date().isoformat() if chunk.fetched_at else "unknown"
        snippet = (
            f"[SOURCE: {chunk.source_url} | type={chunk.source_type} "
            f"| fetched={fetched} | trust={chunk.trust_score:.2f}]\n"
            f"{chunk.chunk_text}\n"
        )
        estimated_tokens = max(len(snippet) // 4, 1)
        if token_count + estimated_tokens > max_tokens:
            break
        context_parts.append(snippet)
        token_count += estimated_tokens

    return "\n---\n".join(context_parts)
