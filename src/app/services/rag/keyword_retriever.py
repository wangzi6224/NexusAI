from time import perf_counter
from typing import Any

from src.app.services.keyword_store import PgKeywordStore


class KeywordRetriever:
    def __init__(self) -> None:
        self.keyword_store = PgKeywordStore()

    def search(
        self,
        query: str,
        top_k: int = 20,
    ) -> dict[str, Any]:
        start = perf_counter()

        chunks = self.keyword_store.search_keyword_chunks(
            query=query,
            top_k=top_k,
        )

        normalized_chunks: list[dict[str, Any]] = []

        for index, chunk in enumerate(chunks):
            normalized_chunks.append(
                {
                    **chunk,
                    "keyword_rank": index + 1,
                    "keyword_score": round(float(chunk.get("keyword_score") or 0), 4),
                    "retrieval_source": "keyword",
                }
            )

        return {
            "query": query,
            "chunks": normalized_chunks,
            "trace": {
                "keyword_top_k": top_k,
                "keyword_count": len(normalized_chunks),
                "keyword_latency_ms": int((perf_counter() - start) * 1000),
            },
        }
