from time import perf_counter
from typing import Any

from src.app.config import get_embedding_model, get_settings
from src.app.services.embedding.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from src.app.services.vector_store import PgVectorStore
from src.app.services.rag.reranker import RagReranker


class RagRetriever:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embedding_provider = SentenceTransformerEmbeddingProvider()
        self.vector_store = PgVectorStore()
        self.reranker = RagReranker()

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        candidate_k: int | None = None,
        rerank_top_n: int | None = None,
        rerank_enabled: bool | None = None,
    ) -> dict[str, Any]:
        """
        分两段检索，先从向量数据库中检索出candidate_k个候选项，
        再对这candidate_k个候选项进行rerank，返回top_k个结果。

        Args:
            query (str): 查询文本
            top_k (int, optional): 返回的最相似结果数量。默认值为5。
            score_threshold (float, optional): 相似度阈值，低于该阈值的结果将被过滤。默认值为0.3。
            candidate_k (int | None, optional): 向量数据库检索的候选项数量。默认值为None。
            rerank_top_n (int | None, optional): 重新排序的候选项数量。默认值为None。
            rerank_enabled (bool | None, optional): 是否启用重新排序。默认值为None。

        Returns:
            dict[str, Any]: 检索结果，包括查询文本、嵌入模型、候选项、重新排序结果等信息。
        """

        embedding_model = get_embedding_model()

        # 向量数据库的candidate_k和reranker的top_n需要配合使用，确保有足够的候选项进行rerank
        final_candidate_k = candidate_k or self.settings.rag_candidate_k
        final_top_n = rerank_top_n or top_k

        if final_candidate_k < final_top_n:
            # 如果candidate_k小于top_n，则调整candidate_k为top_n的值，确保有足够的候选项进行rerank
            final_candidate_k = final_top_n

        embedding_start = perf_counter()
        query_embedding = self.embedding_provider.embed_text(query)
        embedding_latency_ms = int((perf_counter() - embedding_start) * 1000)

        retrieval_start = perf_counter()
        candidate_chunks = self.vector_store.search_similar_chunks(
            query_embedding=query_embedding,
            top_k=final_candidate_k,  # 这里使用final_candidate_k，确保有足够的候选项进行rerank
            score_threshold=score_threshold,
        )
        retrieval_latency_ms = int((perf_counter() - retrieval_start) * 1000)

        # 规范化候选项，确保distance和score字段存在且格式正确
        normalized_candidates = [
            {
                **chunk,
                "distance": round(float(chunk["distance"]), 4),
                "score": round(float(chunk["score"]), 4),
            }
            for chunk in candidate_chunks
        ]

        # 判断是否开启了rerank，在.env文件中配置
        should_rerank = (
            self.settings.reranker_enabled if rerank_enabled is None else rerank_enabled
        )

        if not should_rerank:
            # 如果关了，就原路返回，不扯蛋了
            chunks = self._add_no_rerank_rank(normalized_candidates[:final_top_n])

            return {
                "query": query,
                "embedding_model": embedding_model,
                "top_k": top_k,
                "candidate_k": final_candidate_k,
                "rerank_top_n": final_top_n,
                "score_threshold": score_threshold,
                "chunks": chunks,
                "trace": {  # 这字段以后方便观测和调试用的，不然每次都要打日志，麻烦死了
                    "embedding_latency_ms": embedding_latency_ms,
                    "retrieval_latency_ms": retrieval_latency_ms,
                    "candidate_count": len(normalized_candidates),
                    "rerank_enabled": False,
                    "rerank_model": None,
                    "rerank_latency_ms": 0,
                    "rerank_fallback_reason": "RERANK_DISABLED",
                },
            }

        rerank_result = self.reranker.rerank(
            query=query,
            chunks=normalized_candidates,
            top_n=final_top_n,
        )

        return {
            "query": query,
            "embedding_model": embedding_model,
            "top_k": top_k,
            "candidate_k": final_candidate_k,
            "rerank_top_n": final_top_n,
            "score_threshold": score_threshold,
            "chunks": rerank_result["chunks"],
            "trace": {  # 同理
                "embedding_latency_ms": embedding_latency_ms,
                "retrieval_latency_ms": retrieval_latency_ms,
                "candidate_count": len(normalized_candidates),
                **rerank_result["trace"],
            },
        }

    def _add_no_rerank_rank(
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
