from __future__ import annotations

from typing import Any, cast

from src.app.config import get_embedding_model
from src.app.db import get_connection
from src.app.services.embedding_service import get_embedding_service
from src.app.services.memory.long_term_store import LongTermMemoryStore


class LongTermMemoryEmbeddingService:
    def __init__(self) -> None:
        self.embedding_service = get_embedding_service()
        self.store = LongTermMemoryStore()

    def embed_pending(self, limit: int = 100) -> dict[str, Any]:
        """pending的记忆项进行批量嵌入，并更新数据库中的状态和嵌入结果。"""
        items = self._list_pending(limit=limit)

        if not items:
            return {
                "total": 0,
                "embedded": 0,
                "failed": 0,
                "embedding_model": get_embedding_model(),
                "status": "completed",
            }

        texts = [item["content"] for item in items]
        ids = [item["id"] for item in items]

        embedded = 0
        failed = 0
        embedding_model = get_embedding_model()

        try:
            embeddings = self.embedding_service.provider.embed_texts(texts)

            for memory_id, embedding in zip(ids, embeddings):
                self.store.update_embedding(
                    memory_id=memory_id,
                    embedding=embedding,
                    embedding_model=embedding_model,
                )
                embedded += 1

        except Exception as exc:
            failed = len(items) - embedded
            self._mark_failed(ids[embedded:], str(exc))

        return {
            "total": len(items),
            "embedded": embedded,
            "failed": failed,
            "embedding_model": embedding_model,
            "status": "completed" if failed == 0 else "failed",
        }

    def _list_pending(self, limit: int) -> list[dict[str, Any]]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, content
                    FROM memory_items
                    WHERE status = 'active'
                      AND embedding_status = 'pending'
                    ORDER BY created_at ASC
                    LIMIT %(limit)s
                    """,
                    {"limit": limit},
                )
                rows = cur.fetchall()

        return [cast(dict[str, Any], row) for row in rows]

    def _mark_failed(self, memory_ids: list[str], error_message: str) -> None:
        if not memory_ids:
            return

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE memory_items
                    SET
                        embedding_status = 'failed',
                        embedding_error = %(error_message)s,
                        updated_at = NOW()
                    WHERE id = ANY(%(ids)s)
                    """,
                    {
                        "ids": memory_ids,
                        "error_message": error_message,
                    },
                )

            conn.commit()
