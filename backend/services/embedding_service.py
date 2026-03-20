import asyncio
import hashlib
import random
from collections.abc import Sequence

from loguru import logger

from backend.config import settings

try:
    from fastembed import TextEmbedding
except ImportError:  # pragma: no cover - dependency may be intentionally absent in some environments
    TextEmbedding = None


class EmbeddingService:
    def __init__(self, model: str, dimensions: int = 1536):
        self.model = model
        self.dimensions = dimensions
        self._embedder = TextEmbedding(model_name=model) if TextEmbedding is not None else None
        if self._embedder is None:
            logger.warning("embedding_fastembed_unavailable | model={} fallback=deterministic", self.model)

    async def embed(self, text: str) -> list[float]:
        vectors = await self._embed_batch_with_fallback([text])
        return vectors[0]

    async def embed_batch(self, texts: Sequence[str], batch_size: int = 100) -> list[list[float]]:
        if not texts:
            return []

        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            vectors.extend(await self._embed_batch_with_fallback(batch))
        return vectors

    async def _embed_batch_with_fallback(self, texts: Sequence[str]) -> list[list[float]]:
        if self._embedder is None:
            return [self._deterministic_vector(text) for text in texts]

        vectors = await asyncio.to_thread(self._embed_fastembed_sync, list(texts))
        return [self._normalize_dimensions(vector) for vector in vectors]

    def _embed_fastembed_sync(self, texts: list[str]) -> list[list[float]]:
        assert self._embedder is not None
        # fastembed returns an iterator of numpy arrays.
        return [[float(value) for value in row] for row in self._embedder.embed(texts)]

    def _normalize_dimensions(self, vector: list[float]) -> list[float]:
        current = len(vector)
        if current == self.dimensions:
            return vector
        if current > self.dimensions:
            return vector[: self.dimensions]
        return vector + [0.0] * (self.dimensions - current)

    def _deterministic_vector(self, text: str) -> list[float]:
        seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")
        rng = random.Random(seed)
        return [rng.uniform(-1.0, 1.0) for _ in range(self.dimensions)]


embedding_service = EmbeddingService(
    model=settings.embedding_model,
    dimensions=settings.embedding_dimensions,
)


def build_embedding_service() -> EmbeddingService:
    return embedding_service
