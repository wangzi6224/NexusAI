from time import perf_counter
from typing import Any

from src.app.config import get_embedding_model
from src.app.services.embedding.sentence_transformer_provider import (
    SentenceTransformerEmbeddingProvider,
)
from src.app.services.vector_store import PgVectorStore
from src.app.services.rag.keyword_retriever import KeywordRetriever
from src.app.services.rag.rank_fusion import reciprocal_rank_fusion
from src.app.services.rag.mmr import select_mmr
from src.app.services.rag.reranker import RagReranker


class HybridRetriever:
    def __init__(self) -> None:
        self.embedding_provider = SentenceTransformerEmbeddingProvider()
        self.vector_store = PgVectorStore()
        self.keyword_retriever = KeywordRetriever()
        self.reranker = RagReranker()

    def search(
        self,
        query: str,
        vector_top_k: int = 30,
        keyword_top_k: int = 30,
        fusion_top_k: int = 20,
        final_top_k: int = 5,
        score_threshold: float = 0.3,
        enable_mmr: bool = True,
        enable_rerank: bool = True,
    ) -> dict[str, Any]:
        # 记录整个检索流程的起始时间，用于输出总延迟
        total_start = perf_counter()

        # 1. 计算 query 的向量表示
        embedding_start = perf_counter()
        query_embedding = self.embedding_provider.embed_text(query)
        embedding_latency_ms = int((perf_counter() - embedding_start) * 1000)

        # 2. 向量检索：使用向量数据库搜索最相似的文本片段
        vector_start = perf_counter()
        vector_chunks = self.vector_store.search_similar_chunks(
            query_embedding=query_embedding,
            top_k=vector_top_k,
            score_threshold=score_threshold,
        )
        vector_latency_ms = int((perf_counter() - vector_start) * 1000)

        # 绑定向量检索结果的排名信息和来源标签，便于后续融合和分析
        for index, chunk in enumerate(vector_chunks):
            chunk["vector_rank"] = index + 1
            chunk["vector_score"] = chunk.get("score")
            chunk["retrieval_source"] = "vector"

        # 3. 关键词检索：使用关键词匹配补充向量检索结果
        keyword_result = self.keyword_retriever.search(
            query=query,
            top_k=keyword_top_k,
        )
        keyword_chunks = keyword_result["chunks"]

        # 4. 排名融合：将向量检索结果和关键词检索结果融合成一个候选列表
        fusion_start = perf_counter()
        fused_chunks = reciprocal_rank_fusion(
            ranked_lists=[vector_chunks, keyword_chunks],
            top_k=fusion_top_k,
        )
        fusion_latency_ms = int((perf_counter() - fusion_start) * 1000)

        # 5. MMR 去重/多样性选择：从融合结果中挑选更优、多样化的候选片段
        mmr_start = perf_counter()
        if enable_mmr:
            candidate_chunks = select_mmr(
                chunks=fused_chunks,
                top_k=fusion_top_k,
            )
        else:
            candidate_chunks = fused_chunks[:fusion_top_k]

        mmr_latency_ms = int((perf_counter() - mmr_start) * 1000)

        # 6. 重排序：可选地对候选结果进行模型 rerank，提高最终结果质量
        if enable_rerank:
            rerank_result = self.reranker.rerank(
                query=query,
                chunks=candidate_chunks,
                top_n=final_top_k,
            )
            final_chunks = rerank_result["chunks"]
            rerank_trace = rerank_result["trace"]
        else:
            final_chunks = candidate_chunks[:final_top_k]
            rerank_trace = {
                "rerank_enabled": False,
                "rerank_model": None,
                "rerank_latency_ms": 0,
                "rerank_fallback_reason": "RERANK_DISABLED",
            }

        # 7. 返回结果与诊断 trace，包含检索参数、计数和各阶段延迟
        return {
            "query": query,
            "embedding_model": get_embedding_model(),
            "retrieval_mode": "hybrid_rrf_mmr_rerank",
            "chunks": final_chunks,
            "trace": {
                "retrieval_mode": "hybrid_rrf_mmr_rerank",
                "vector_top_k": vector_top_k,
                "keyword_top_k": keyword_top_k,
                "fusion_top_k": fusion_top_k,
                "final_top_k": final_top_k,
                "vector_count": len(vector_chunks),
                "keyword_count": len(keyword_chunks),
                "fusion_count": len(fused_chunks),
                "final_count": len(final_chunks),
                "embedding_latency_ms": embedding_latency_ms,
                "vector_latency_ms": vector_latency_ms,
                "keyword_latency_ms": keyword_result["trace"]["keyword_latency_ms"],
                "fusion_latency_ms": fusion_latency_ms,
                "mmr_enabled": enable_mmr,
                "mmr_latency_ms": mmr_latency_ms,
                "total_retrieval_latency_ms": int(
                    (perf_counter() - total_start) * 1000
                ),
                **rerank_trace,
            },
        }
