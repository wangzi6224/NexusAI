import json

from src.app.services.rag.retriever import RagRetriever
from typing import Any


class RagDebugService:
    def __init__(self):
        self.retriever = RagRetriever()

    def compare_search(self, message: str):
        without_rerank = self.retriever.search(
            query=message,
            top_k=5,
            score_threshold=0.3,
            candidate_k=20,
            rerank_top_n=5,
            rerank_enabled=False,
        )

        with_rerank = self.retriever.search(
            query=message,
            top_k=5,
            score_threshold=0.3,
            candidate_k=20,
            rerank_top_n=5,
            rerank_enabled=True,
        )

        compare = self._build_rank_compare(
            with_rerank["chunks"],
        )

        return {
            "query": message,
            "without_rerank": without_rerank,
            "with_rerank": with_rerank,
            "compare": compare,
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
