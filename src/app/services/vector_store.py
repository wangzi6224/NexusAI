import json
from typing import Any

from pgvector import Vector
from pgvector.psycopg import register_vector

from src.app.db import get_connection


class PgVectorStore:
    def _register_vector(self, conn) -> None:
        register_vector(conn)

    def sync_chunks_from_json(self, chunks: list[dict[str, Any]]) -> int:
        synced_count = 0

        with get_connection() as conn:
            self._register_vector(conn)

            with conn.cursor() as cur:
                for chunk in chunks:
                    cur.execute(
                        """
                        INSERT INTO document_chunks (
                            id,
                            document_id,
                            chunk_index,
                            heading,
                            content,
                            char_count,
                            estimated_tokens,
                            metadata,
                            updated_at
                        )
                        VALUES (
                            %(id)s,
                            %(document_id)s,
                            %(chunk_index)s,
                            %(heading)s,
                            %(content)s,
                            %(char_count)s,
                            %(estimated_tokens)s,
                            %(metadata)s::jsonb,
                            NOW()
                        )
                        ON CONFLICT (id) DO UPDATE SET
                            document_id = EXCLUDED.document_id,
                            chunk_index = EXCLUDED.chunk_index,
                            heading = EXCLUDED.heading,
                            content = EXCLUDED.content,
                            char_count = EXCLUDED.char_count,
                            estimated_tokens = EXCLUDED.estimated_tokens,
                            metadata = EXCLUDED.metadata,
                            updated_at = NOW()
                        """,
                        {
                            "id": chunk["id"],
                            "document_id": chunk["document_id"],
                            "chunk_index": chunk["chunk_index"],
                            "heading": chunk.get("heading"),
                            "content": chunk["content"],
                            "char_count": chunk["char_count"],
                            "estimated_tokens": chunk["estimated_tokens"],
                            "metadata": json.dumps(
                                chunk.get("metadata") or {},
                                ensure_ascii=False,
                            ),
                        },
                    )
                    synced_count += 1

            conn.commit()

        return synced_count

    def list_chunks_by_document(self, document_id: str) -> list[dict[str, Any]]:
        with get_connection() as conn:
            self._register_vector(conn)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM document_chunks
                    WHERE document_id = %(document_id)s
                    ORDER BY chunk_index ASC
                    """,
                    {"document_id": document_id},
                )
                return [dict(row) for row in cur.fetchall()]

    def list_pending_chunks(self, limit: int = 100) -> list[dict[str, Any]]:
        with get_connection() as conn:
            self._register_vector(conn)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM document_chunks
                    WHERE embedding_status = 'pending'
                    ORDER BY created_at ASC
                    LIMIT %(limit)s
                    """,
                    {"limit": limit},
                )
                return [dict(row) for row in cur.fetchall()]

    def mark_chunks_processing(self, chunk_ids: list[str]) -> None:
        if not chunk_ids:
            return

        with get_connection() as conn:
            self._register_vector(conn)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE document_chunks
                    SET embedding_status = 'processing',
                        embedding_error = NULL,
                        embedding_updated_at = NOW(),
                        updated_at = NOW()
                    WHERE id = ANY(%(chunk_ids)s)
                    """,
                    {"chunk_ids": chunk_ids},
                )

            conn.commit()

    def update_chunk_embedding(
        self,
        chunk_id: str,
        embedding: list[float],
        embedding_model: str,
    ) -> None:
        with get_connection() as conn:
            self._register_vector(conn)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE document_chunks
                    SET embedding = %(embedding)s,
                        embedding_model = %(embedding_model)s,
                        embedding_status = 'completed',
                        embedding_error = NULL,
                        embedding_updated_at = NOW(),
                        updated_at = NOW()
                    WHERE id = %(chunk_id)s
                    """,
                    {
                        "chunk_id": chunk_id,
                        "embedding": Vector(embedding),
                        "embedding_model": embedding_model,
                    },
                )

            conn.commit()

    def mark_chunk_failed(self, chunk_id: str, error_message: str) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE document_chunks
                    SET embedding_status = 'failed',
                        embedding_error = %(error_message)s,
                        embedding_updated_at = NOW(),
                        updated_at = NOW()
                    WHERE id = %(chunk_id)s
                    """,
                    {
                        "chunk_id": chunk_id,
                        "error_message": error_message,
                    },
                )

            conn.commit()

    def get_document_embedding_status(self, document_id: str) -> list[dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id AS chunk_id,
                        chunk_index,
                        embedding_status,
                        embedding_model,
                        embedding_error,
                        embedding_updated_at
                    FROM document_chunks
                    WHERE document_id = %(document_id)s
                    ORDER BY chunk_index ASC
                    """,
                    {"document_id": document_id},
                )
                return [dict(row) for row in cur.fetchall()]

    def search_similar_chunks(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        with get_connection() as conn:
            self._register_vector(conn)

            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id AS chunk_id,
                        document_id,
                        chunk_index,
                        heading,
                        content,
                        embedding <=> %(query_embedding)s AS distance,
                        1 - (embedding <=> %(query_embedding)s) AS score
                    FROM document_chunks
                    WHERE embedding IS NOT NULL
                      AND embedding_status = 'completed'
                    ORDER BY embedding <=> %(query_embedding)s
                    LIMIT %(top_k)s
                    """,
                    {
                        "query_embedding": Vector(query_embedding),
                        "top_k": top_k,
                    },
                )
                return [dict(row) for row in cur.fetchall()]
