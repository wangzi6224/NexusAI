from src.app.services.rag.retriever import RagRetriever
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from time import perf_counter


class RagDebugService:
    def __init__(self):
        self.retriever = RagRetriever()

    def compare_search(self, query: str):
        start_time = perf_counter()
        params = {
            "query": query,
            "top_k": 5,
            "score_threshold": 0.3,
            "candidate_k": 20,
            "rerank_top_n": 5,
        }
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_without = executor.submit(
                self.retriever.search,
                **params,
                rerank_enabled=False,
            )
            future_with = executor.submit(
                self.retriever.search,
                **params,
                rerank_enabled=True,
            )

            without_rerank = future_without.result()
            with_rerank = future_with.result()

        compare = self._build_rank_compare(with_rerank["chunks"])
        latency_ms = int((perf_counter() - start_time) * 1000)

        return {
            "query": query,
            "without_rerank": without_rerank,
            "with_rerank": with_rerank,
            "compare": compare,
            "latency_ms": latency_ms,
        }

    def _build_rank_compare(
        self,
        chunks: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        result = []

        for chunk in chunks:
            retrieval_rank = chunk.get("retrieval_rank")
            rerank_rank = chunk.get("rerank_rank")

            rank_change = None

            if retrieval_rank is not None and rerank_rank is not None:
                rank_change = retrieval_rank - rerank_rank

            result.append(
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "filename": chunk.get("filename"),
                    "retrieval_rank": retrieval_rank,
                    "rerank_rank": rerank_rank,
                    "rank_change": rank_change,
                    "vector_score": chunk.get("vector_score"),
                    "rerank_score": chunk.get("rerank_score"),
                }
            )

        return result
