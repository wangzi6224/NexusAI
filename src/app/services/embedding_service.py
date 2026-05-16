from functools import lru_cache
from typing import Any, Literal

from src.app.config import (
    get_embedding_batch_size,
    get_embedding_dimension,
    get_embedding_model,
)
from src.app.document_store import load_document_chunks
from src.app.exceptions import AppError
from src.app.services.embedding.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from src.app.services.vector_store import PgVectorStore


class EmbeddingService:
    def __init__(self) -> None:
        self.provider = SentenceTransformerEmbeddingProvider()
        self.vector_store = PgVectorStore()

    def test_embedding(self, text: str) -> dict[str, Any]:
        vector = self.provider.embed_text(text)
        self._validate_dimension(vector)

        vector_norm = sum(value * value for value in vector) ** 0.5

        return {
            "text": text,
            "embedding_model": get_embedding_model(),
            "dimension": len(vector),
            "vector_preview": [round(value, 4) for value in vector[:5]],
            "vector_norm": round(vector_norm, 4),
        }

    def embed_document(self, document_id: str) -> dict[str, Any]:
        all_chunks = load_document_chunks()
        self.vector_store.sync_chunks_from_json(all_chunks)

        chunks = self.vector_store.list_chunks_by_document(document_id)

        if not chunks:
            raise AppError(
                code="DOCUMENT_CHUNKS_NOT_FOUND",
                message="该文档没有可向量化的 chunks",
                detail=f"document_id={document_id}",
                status_code=404,
            )

        return self._embed_chunks(
            chunks=chunks,
            document_id=document_id,
        )

    def embed_all_pending(self) -> dict[str, Any]:
        all_chunks = load_document_chunks()
        self.vector_store.sync_chunks_from_json(all_chunks)

        limit = get_embedding_batch_size()
        chunks = self.vector_store.list_pending_chunks(limit=limit)

        result = self._embed_chunks(chunks=chunks)

        return {
            "total_chunks": result["total_chunks"],
            "embedded_chunks": result["embedded_chunks"],
            "failed_chunks": result["failed_chunks"],
            "embedding_model": result["embedding_model"],
            "status": result["status"],
        }

    def get_document_embedding_status(self, document_id: str) -> dict[str, Any]:
        items = self.vector_store.get_document_embedding_status(document_id)

        return {
            "document_id": document_id,
            "items": [
                {
                    **item,
                    "embedding_updated_at": (
                        item["embedding_updated_at"].isoformat()
                        if item.get("embedding_updated_at")
                        else None
                    ),
                }
                for item in items
            ],
        }

    def search_debug(self, query: str, top_k: int = 5) -> dict[str, Any]:
        query_embedding = self.provider.embed_text(query)
        self._validate_dimension(query_embedding)

        items = self.vector_store.search_similar_chunks(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        return {
            "query": query,
            "embedding_model": get_embedding_model(),
            "top_k": top_k,
            "items": [
                {
                    **item,
                    "distance": round(float(item["distance"]), 4),
                    "score": round(float(item["score"]), 4),
                }
                for item in items
            ],
        }

    def _embed_chunks(
        self,
        chunks: list[dict[str, Any]],
        document_id: str | None = None,
    ) -> dict[str, Any]:
        total_chunks = len(chunks)
        embedded_chunks = 0
        failed_chunks = 0

        if not chunks:
            return {
                "document_id": document_id,
                "total_chunks": 0,
                "embedded_chunks": 0,
                "failed_chunks": 0,
                "embedding_model": get_embedding_model(),
                "status": "completed",
            }

        chunk_ids = [chunk["id"] for chunk in chunks]
        texts = [chunk["content"] for chunk in chunks]

        self.vector_store.mark_chunks_processing(chunk_ids)

        try:
            embeddings = self.provider.embed_texts(texts)

            for chunk, embedding in zip(chunks, embeddings):
                self._validate_dimension(embedding)

                self.vector_store.update_chunk_embedding(
                    chunk_id=chunk["id"],
                    embedding=embedding,
                    embedding_model=get_embedding_model(),
                )
                embedded_chunks += 1

        except Exception as exc:
            failed_chunks = total_chunks - embedded_chunks

            for chunk in chunks[embedded_chunks:]:
                self.vector_store.mark_chunk_failed(
                    chunk_id=chunk["id"],
                    error_message=str(exc),
                )

        status: Literal["completed"] | Literal["failed"] = (
            "completed" if failed_chunks == 0 else "failed"
        )

        return {
            "document_id": document_id,
            "total_chunks": total_chunks,
            "embedded_chunks": embedded_chunks,
            "failed_chunks": failed_chunks,
            "embedding_model": get_embedding_model(),
            "status": status,
        }

    def _validate_dimension(self, vector: list[float]) -> None:
        expected_dimension = get_embedding_dimension()
        actual_dimension = len(vector)

        if actual_dimension != expected_dimension:
            raise AppError(
                code="EMBEDDING_DIMENSION_MISMATCH",
                message="Embedding 维度和配置不一致",
                detail=f"expected={expected_dimension}, actual={actual_dimension}",
                status_code=500,
            )


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()
