def _keyword_overlap(a: str, b: str) -> float:
    a_words = set(a.lower().split())
    b_words = set(b.lower().split())
    if not a_words:
        return 0.0
    return len(a_words & b_words) / len(a_words)


async def find_supporting_chunks(claim: str, chunks: list[dict], top_k: int = 3) -> list[dict]:
    if not chunks:
        return []

    ranked = sorted(
        chunks,
        key=lambda chunk: _keyword_overlap(claim, str(chunk.get("chunk_text", ""))),
        reverse=True,
    )
    return ranked[:top_k]
