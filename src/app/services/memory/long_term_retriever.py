from __future__ import annotations

import json
from time import perf_counter
from typing import Any, cast

from psycopg.sql import SQL

from src.app.db import get_connection
from src.app.services.embedding_service import get_embedding_service
from src.app.services.memory.long_term_ranker import LongTermMemoryRanker
from src.app.services.memory.long_term_schemas import (
    LongTermMemoryItem,
    LongTermMemoryRetrievalResult,
    LongTermMemorySearchRequest,
    RetrievedLongTermMemory,
)


class LongTermMemoryRetriever:
    def __init__(self) -> None:
        self.embedding_service = get_embedding_service()
        self.ranker = LongTermMemoryRanker()

    def retrieve(
        self,
        request: LongTermMemorySearchRequest,
    ) -> LongTermMemoryRetrievalResult:
        start = perf_counter()

        query_embedding = self.embedding_service.provider.embed_text(request.query)

        rows = self._search_vector(
            request=request,
            query_embedding=query_embedding,
            candidate_k=max(request.top_k * 4, 20),
        )

        retrieved: list[RetrievedLongTermMemory] = []

        for row in rows:
            item = self._row_to_item(row)
            similarity_score = float(row["similarity_score"])

            # 计算综合评分，考虑相似度、重要性、置信度、最近访问时间和访问频率等因素
            final_score = self.ranker.score(
                similarity_score=similarity_score,
                item=item,
            )

            if final_score < request.min_score:
                # 如果综合评分低于阈值，则跳过该记忆项
                continue

            retrieved.append(
                RetrievedLongTermMemory(
                    item=item,
                    score=final_score,
                    rank=0,
                    reason=(
                        f"similarity={similarity_score:.3f}, "
                        f"importance={item.importance:.2f}, "
                        f"confidence={item.confidence:.2f}"
                    ),
                )
            )

        retrieved.sort(key=lambda item: item.score, reverse=True)
        retrieved = retrieved[: request.top_k]

        for index, item in enumerate(retrieved, start=1):
            item.rank = index

        latency_ms = int((perf_counter() - start) * 1000)

        return LongTermMemoryRetrievalResult(
            query=request.query,
            items=retrieved,
            latency_ms=latency_ms,
            trace={
                "query": request.query,
                "candidate_count": len(rows),
                "returned_count": len(retrieved),
                "top_k": request.top_k,
                "memory_types": request.memory_types,
                "latency_ms": latency_ms,
            },
        )

    def _search_vector(
        self,
        *,
        request: LongTermMemorySearchRequest,
        query_embedding: list[float],
        candidate_k: int,
    ) -> list[dict[str, Any]]:
        """在数据库中执行向量检索，返回候选记忆项列表
        - 只检索状态为 active 的记忆项
        - 只检索 embedding 不为空的记忆项
        - 只检索未过期的记忆项（expires_at 为空或大于当前时间）
        - 如果提供了 workspace_id，则检索 workspace_id 匹配或为 NULL 的记忆项
        - 如果提供了 memory_types，则检索 memory_type 在指定列表中的记忆项
        """
        conditions = [
            "user_id = %(user_id)s",
            "status = 'active'",
            "embedding IS NOT NULL",
            "(expires_at IS NULL OR expires_at > NOW())",
        ]

        params: dict[str, Any] = {
            "user_id": request.user_id,
            "query_embedding": query_embedding,
            "candidate_k": candidate_k,
        }

        if request.workspace_id:
            conditions.append(
                "(workspace_id = %(workspace_id)s OR workspace_id IS NULL)"
            )
            params["workspace_id"] = request.workspace_id

        if request.memory_types:
            conditions.append("memory_type = ANY(%(memory_types)s)")
            params["memory_types"] = request.memory_types

        where_sql = " AND ".join(conditions)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    SQL("""
                    SELECT
                        *,
                        1 - (embedding <=> %(query_embedding)s::vector) AS similarity_score
                    FROM memory_items
                    WHERE {where_sql}
                    ORDER BY embedding <=> %(query_embedding)s::vector
                    LIMIT %(candidate_k)s
                    """).format(where_sql=SQL(cast(Any, where_sql))),
                    params,
                )
                rows = cur.fetchall()

        return [cast(dict[str, Any], row) for row in rows]

    def _row_to_item(self, row: dict[str, Any]) -> LongTermMemoryItem:
        data = dict(row)

        if isinstance(data.get("metadata"), str):
            data["metadata"] = json.loads(data["metadata"])

        return LongTermMemoryItem(**data)
