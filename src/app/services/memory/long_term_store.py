from __future__ import annotations

import json
import uuid
from typing import Any, cast

from psycopg.sql import SQL

from src.app.db import get_connection
from src.app.services.memory.long_term_schemas import (
    LongTermMemoryCreate,
    LongTermMemoryItem,
    LongTermMemoryUpdate,
)


def normalize_memory_content(content: str) -> str:
    return " ".join(content.strip().lower().split())


class LongTermMemoryStore:
    """长期记忆仓储。

    职责：
    - 数据库读写
    - soft delete
    - access_count 更新
    - embedding 状态更新

    不负责：
    - 判断是否应该保存
    - LLM 抽取
    - 语义去重策略
    """

    def create(self, payload: LongTermMemoryCreate) -> LongTermMemoryItem:
        memory_id = str(uuid.uuid4())
        normalized_content = normalize_memory_content(payload.content)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL("""
                    INSERT INTO memory_items (
                        id,
                        user_id,
                        workspace_id,
                        conversation_id,
                        source_message_id,
                        source_run_id,
                        memory_type,
                        content,
                        normalized_content,
                        importance,
                        confidence,
                        expires_at,
                        metadata,
                        status,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %(id)s,
                        %(user_id)s,
                        %(workspace_id)s,
                        %(conversation_id)s,
                        %(source_message_id)s,
                        %(source_run_id)s,
                        %(memory_type)s,
                        %(content)s,
                        %(normalized_content)s,
                        %(importance)s,
                        %(confidence)s,
                        %(expires_at)s,
                        %(metadata)s::jsonb,
                        'active',
                        NOW(),
                        NOW()
                    )
                    RETURNING *
                    """),
                    {
                        "id": memory_id,
                        "user_id": payload.user_id,
                        "workspace_id": payload.workspace_id,
                        "conversation_id": payload.conversation_id,
                        "source_message_id": payload.source_message_id,
                        "source_run_id": payload.source_run_id,
                        "memory_type": payload.memory_type,
                        "content": payload.content.strip(),
                        "normalized_content": normalized_content,
                        "importance": payload.importance,
                        "confidence": payload.confidence,
                        "expires_at": payload.expires_at,
                        "metadata": json.dumps(payload.metadata, ensure_ascii=False),
                    },
                )
                row = cur.fetchone()

            conn.commit()

        return self._row_to_item(cast(dict[str, Any], row))

    def get(self, memory_id: str) -> LongTermMemoryItem | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL("""
                    SELECT *
                    FROM memory_items
                    WHERE id = %(id)s
                      AND status <> 'deleted'
                    """),
                    {"id": memory_id},
                )
                row = cur.fetchone()

        if row is None:
            return None

        return self._row_to_item(cast(dict[str, Any], row))

    def list(
        self,
        *,
        user_id: str = "default_user",
        memory_type: str | None = None,
        status: str = "active",
        limit: int = 50,
        offset: int = 0,
    ) -> list[LongTermMemoryItem]:
        conditions = ["user_id = %(user_id)s", "status = %(status)s"]
        params: dict[str, Any] = {
            "user_id": user_id,
            "status": status,
            "limit": limit,
            "offset": offset,
        }

        if memory_type:
            conditions.append("memory_type = %(memory_type)s")
            params["memory_type"] = memory_type

        where_sql = " AND ".join(conditions)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL("""
                    SELECT *
                    FROM memory_items
                    WHERE {where_sql}
                    ORDER BY importance DESC, updated_at DESC
                    LIMIT %(limit)s OFFSET %(offset)s
                    """).format(where_sql=SQL(cast(Any, where_sql))),
                    params,
                )
                rows = cur.fetchall()

        return [self._row_to_item(cast(dict[str, Any], row)) for row in rows]

    def update(
        self,
        memory_id: str,
        payload: LongTermMemoryUpdate,
    ) -> LongTermMemoryItem:
        normalized_content = (
            normalize_memory_content(payload.content)
            if payload.content is not None
            else None
        )

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL("""
                    UPDATE memory_items
                    SET
                        content = COALESCE(%(content)s, content),
                        normalized_content = COALESCE(%(normalized_content)s, normalized_content),
                        importance = COALESCE(%(importance)s, importance),
                        confidence = COALESCE(%(confidence)s, confidence),
                        status = COALESCE(%(status)s, status),
                        expires_at = COALESCE(%(expires_at)s, expires_at),
                        metadata = COALESCE(%(metadata)s::jsonb, metadata),
                        embedding_status = CASE
                            WHEN %(content)s IS NOT NULL THEN 'pending'
                            ELSE embedding_status
                        END,
                        updated_at = NOW()
                    WHERE id = %(id)s
                    RETURNING *
                    """),
                    {
                        "id": memory_id,
                        "content": payload.content.strip() if payload.content else None,
                        "normalized_content": normalized_content,
                        "importance": payload.importance,
                        "confidence": payload.confidence,
                        "status": payload.status,
                        "expires_at": payload.expires_at,
                        "metadata": (
                            json.dumps(payload.metadata, ensure_ascii=False)
                            if payload.metadata is not None
                            else None
                        ),
                    },
                )
                row = cur.fetchone()

            conn.commit()

        if row is None:
            raise ValueError(f"memory not found: {memory_id}")

        return self._row_to_item(cast(dict[str, Any], row))

    def archive(self, memory_id: str) -> LongTermMemoryItem:
        return self.update(memory_id, LongTermMemoryUpdate(status="archived"))

    def delete(self, memory_id: str) -> LongTermMemoryItem:
        return self.update(memory_id, LongTermMemoryUpdate(status="deleted"))

    def mark_accessed(self, memory_ids: list[str]) -> None:
        if not memory_ids:
            return

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL("""
                    UPDATE memory_items
                    SET
                        access_count = access_count + 1,
                        last_accessed_at = NOW(),
                        updated_at = NOW()
                    WHERE id = ANY(%(ids)s)
                    """),
                    {"ids": memory_ids},
                )

            conn.commit()

    def find_similar_by_text(
        self,
        *,
        user_id: str,
        normalized_content: str,
        memory_type: str | None = None,
        limit: int = 5,
    ) -> list[LongTermMemoryItem]:
        conditions = [
            "user_id = %(user_id)s",
            "status = 'active'",
            "similarity(normalized_content, %(normalized_content)s) > 0.65",
        ]

        params: dict[str, Any] = {
            "user_id": user_id,
            "normalized_content": normalized_content,
            "limit": limit,
        }

        if memory_type:
            conditions.append("memory_type = %(memory_type)s")
            params["memory_type"] = memory_type

        where_sql = " AND ".join(conditions)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL("""
                    SELECT *
                    FROM memory_items
                    WHERE {where_sql}
                    ORDER BY similarity(normalized_content, %(normalized_content)s) DESC
                    LIMIT %(limit)s
                    """).format(where_sql=SQL(cast(Any, where_sql))),
                    params,
                )
                rows = cur.fetchall()

        return [self._row_to_item(cast(dict[str, Any], row)) for row in rows]

    def update_embedding(
        self,
        *,
        memory_id: str,
        embedding: list[float],
        embedding_model: str,
    ) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL("""
                    UPDATE memory_items
                    SET
                        embedding = %(embedding)s,
                        embedding_model = %(embedding_model)s,
                        embedding_status = 'completed',
                        embedding_error = NULL,
                        embedding_updated_at = NOW(),
                        updated_at = NOW()
                    WHERE id = %(memory_id)s
                    """),
                    {
                        "memory_id": memory_id,
                        "embedding": embedding,
                        "embedding_model": embedding_model,
                    },
                )

            conn.commit()

    def _row_to_item(self, row: dict[str, Any]) -> LongTermMemoryItem:
        data = dict(row)

        if isinstance(data.get("metadata"), str):
            data["metadata"] = json.loads(data["metadata"])

        return LongTermMemoryItem(**data)
