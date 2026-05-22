from typing import Any

from src.app.config import get_embedding_model
from src.app.services.embedding.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from src.app.services.vector_store import PgVectorStore


class RagRetriever:
    def __init__(self) -> None:
        self.embedding_provider = SentenceTransformerEmbeddingProvider()
        self.vector_store = PgVectorStore()

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
    ) -> dict[str, Any]:
        embedding_model = get_embedding_model()
        query_embedding = self.embedding_provider.embed_text(query)

        chunks = self.vector_store.search_similar_chunks(
            query_embedding=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        return {
            "query": query,
            "embedding_model": embedding_model,
            "top_k": top_k,
            "score_threshold": score_threshold,
            "chunks": [
                {
                    **chunk,
                    "distance": round(float(chunk["distance"]), 4),
                    "score": round(float(chunk["score"]), 4),
                }
                for chunk in chunks
            ],
        }
