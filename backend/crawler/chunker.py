try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:  # pragma: no cover - fallback for local envs without optional dep
    RecursiveCharacterTextSplitter = None


def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 64) -> list[str]:
    if not text.strip():
        return []

    if RecursiveCharacterTextSplitter is not None:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_text(text)

    chunks: list[str] = []
    start = 0
    step = max(chunk_size - chunk_overlap, 1)
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += step
    return chunks


def estimate_token_count(text: str) -> int:
    return max(len(text) // 4, 1)


def chunk_with_metadata(text: str, source_url: str, entity_id: str | None) -> list[dict]:
    _ = source_url, entity_id
    chunks = chunk_text(text)
    results: list[dict] = []
    cursor = 0

    for index, chunk in enumerate(chunks):
        start = text.find(chunk, cursor)
        if start < 0:
            start = cursor
        end = start + len(chunk)
        cursor = max(end - 64, 0)

        results.append(
            {
                "chunk_text": chunk,
                "chunk_index": index,
                "char_start": start,
                "char_end": end,
                "token_count": estimate_token_count(chunk),
            }
        )

    return results
