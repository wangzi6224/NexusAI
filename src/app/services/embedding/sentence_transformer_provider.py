from __future__ import annotations

from typing import TYPE_CHECKING

from src.app.config import get_embedding_model
from src.app.services.embedding.base import EmbeddingProvider

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str | None = None) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name or get_embedding_model()
        self.model: SentenceTransformer = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> list[float]:
        embeddings: list[list[float]] = self.embed_texts([text])
        return embeddings[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            normalize_embeddings=True,
        )

        return vectors.tolist()

    def dimension(self) -> int:
        dimension = self.model.get_embedding_dimension()
        if dimension is None:
            raise RuntimeError("无法获取 embedding 模型维度")
        return int(dimension)
