from collections.abc import Sequence

from openai import AsyncOpenAI

from backend.config import settings


class EmbeddingService:
    def __init__(self, model: str, dimensions: int = 1536):
        self.model = model
        self.dimensions = dimensions
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def embed(self, text: str) -> list[float]:
        vectors = await self._embed_openai_batch([text])
        return vectors[0]

    async def embed_batch(self, texts: Sequence[str], batch_size: int = 100) -> list[list[float]]:
        if not texts:
            return []

        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            vectors.extend(await self._embed_openai_batch(batch))
        return vectors

    async def _embed_openai_batch(self, texts: Sequence[str]) -> list[list[float]]:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for embeddings")

        response = await self._client.embeddings.create(model=self.model, input=list(texts))
        sorted_rows = sorted(response.data, key=lambda row: row.index)
        vectors = [[float(v) for v in row.embedding] for row in sorted_rows]
        if vectors and len(vectors[0]) != self.dimensions:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.dimensions}, got {len(vectors[0])}"
            )
        return vectors


embedding_service = EmbeddingService(
    model=settings.embedding_model,
    dimensions=settings.embedding_dimensions,
)


def build_embedding_service() -> EmbeddingService:
    return embedding_service
