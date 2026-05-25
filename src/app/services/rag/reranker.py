from __future__ import annotations

from time import perf_counter
from typing import Any

from src.app.config import Settings, get_settings
from src.app.services.rag.reranker_provider import BgeRerankerProvider


class RagReranker:
    """
    RAG 业务精排层。

    它解决的问题不是“模型怎么调用”，而是：
    1. 如何把候选 chunk 转成 passage；
    2. 如何记录原始向量排名；
    3. 如何添加 rerank_score；
    4. 如何重新排序；
    5. 如何 fallback；
    6. 如何返回 trace。
    """

    def __init__(self) -> None:
        self.settings: Settings = get_settings()
        self.provider: BgeRerankerProvider = BgeRerankerProvider()

    def rerank(
        self,
        query: str,
        chunks: list[dict[str, Any]],
        top_n: int,
    ) -> dict[str, Any]:
        start = perf_counter()

        # 如果没有候选 chunk，直接返回空结果和 trace。
        if not chunks:
            return {
                "chunks": [],
                "trace": {
                    "rerank_enabled": self.settings.reranker_enabled,
                    "rerank_model": self.settings.reranker_model,
                    "rerank_latency_ms": 0,
                    "rerank_fallback_reason": None,
                },
            }

        # 如果精排功能关闭了，直接返回原始排名的前 top_n 个 chunk 和 trace。
        if not self.settings.reranker_enabled:
            return {
                "chunks": self._add_default_rank(chunks[:top_n]),
                "trace": {
                    "rerank_enabled": False,
                    "rerank_model": None,
                    "rerank_latency_ms": 0,
                    "rerank_fallback_reason": "RERANKER_DISABLED",
                },
            }

        try:
            max_chars = self.settings.rag_max_rerank_content_chars

            passages = [str(chunk.get("content", ""))[:max_chars] for chunk in chunks]

            scores = self.provider.score(
                query=query,
                passages=passages,
            )

            reranked_chunks: list[dict[str, Any]] = []

            for index, chunk in enumerate(chunks):
                item = {
                    **chunk,
                    # 原始向量检索排名
                    "retrieval_rank": index + 1,
                    # 保留原始向量分数，不要覆盖
                    "vector_score": chunk.get("score"),
                    "vector_distance": chunk.get("distance"),
                    # 新增 reranker 分数
                    "rerank_score": round(float(scores[index]), 4),
                }

                reranked_chunks.append(item)

            reranked_chunks.sort(
                key=lambda item: item["rerank_score"],
                reverse=True,
            )

            for index, chunk in enumerate(reranked_chunks):
                chunk["rerank_rank"] = index + 1

            return {
                "chunks": reranked_chunks[:top_n],
                "trace": {
                    "rerank_enabled": True,
                    "rerank_model": self.settings.reranker_model,
                    "rerank_latency_ms": int((perf_counter() - start) * 1000),
                    "rerank_fallback_reason": None,
                },
            }

        except Exception as exc:
            return {
                "chunks": self._add_default_rank(chunks[:top_n]),
                "trace": {
                    "rerank_enabled": True,
                    "rerank_model": self.settings.reranker_model,
                    "rerank_latency_ms": int((perf_counter() - start) * 1000),
                    "rerank_fallback_reason": f"RERANK_FAILED: {exc}",
                },
            }

    def _add_default_rank(
        self,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []

        for index, chunk in enumerate(chunks):
            result.append(
                {
                    **chunk,
                    "retrieval_rank": index + 1,
                    "rerank_rank": index + 1,
                    "vector_score": chunk.get("score"),
                    "vector_distance": chunk.get("distance"),
                    "rerank_score": None,
                }
            )

        return result
