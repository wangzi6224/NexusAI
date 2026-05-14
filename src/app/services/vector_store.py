import json
from typing import Any

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
