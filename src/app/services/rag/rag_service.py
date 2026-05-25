from time import perf_counter
from typing import Any

from src.app.config import get_ollama_model
from src.app.services.llm.base import LLMResponse
from src.app.services.llm.ollama_provider import OllamaProvider
from src.app.services.rag.prompt_builder import RagPromptBuilder
from src.app.services.rag.retriever import RagRetriever

NO_ANSWER = "根据当前知识库资料，无法确定。"


class RagService:
    def __init__(self) -> None:
        self.retriever = RagRetriever()
        self.prompt_builder = RagPromptBuilder()
        self.llm_provider = OllamaProvider()

    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        candidate_k: int | None = None,
        rerank_top_n: int | None = None,
        rerank_enabled: bool | None = None,
    ) -> dict[str, Any]:
        return self.retriever.search(
            query=query,
            top_k=top_k,
            score_threshold=score_threshold,
            candidate_k=candidate_k,
            rerank_top_n=rerank_top_n,
            rerank_enabled=rerank_enabled,
        )

    def ask(
        self,
        question: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        model: str | None = None,
        candidate_k: int | None = None,
        rerank_top_n: int | None = None,
        rerank_enabled: bool | None = None,
    ) -> dict[str, Any]:
        search_result = self.search(
            query=question,
            top_k=top_k,
            score_threshold=score_threshold,
            candidate_k=candidate_k,
            rerank_top_n=rerank_top_n,
            rerank_enabled=rerank_enabled,
        )

        chunks = search_result["chunks"]
        selected_model = model or get_ollama_model()

        if not chunks:
            return {
                "question": question,
                "answer": NO_ANSWER,
                "sources": [],
                "trace": {
                    "top_k": top_k,
                    "score_threshold": score_threshold,
                    "retrieved_count": 0,
                    "embedding_model": search_result["embedding_model"],
                    "chat_model": selected_model,
                    "provider": "ollama",
                    "latency_ms": 0,
                },
            }

        messages = self.prompt_builder.build(
            question=question,
            chunks=chunks,
        )

        start = perf_counter()
        response: LLMResponse = self.llm_provider.chat(
            messages=messages,
            model=selected_model,
        )
        latency_ms = int((perf_counter() - start) * 1000)

        return {
            "question": question,
            "answer": response.content,
            "sources": self._build_sources(chunks),
            "trace": {
                "top_k": top_k,
                "score_threshold": score_threshold,
                "retrieved_count": len(chunks),
                "embedding_model": search_result["embedding_model"],
                "chat_model": response.model,
                "provider": response.provider,
                "latency_ms": latency_ms,
            },
        }

    def _build_sources(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "heading": chunk.get("heading"),
                "chunk_index": chunk["chunk_index"],
                "vector_score": chunk.get("vector_score"),
                "vector_distance": chunk.get("vector_distance"),
                "retrieval_rank": chunk.get("retrieval_rank"),
                "rerank_score": chunk.get("rerank_score"),
                "rerank_rank": chunk.get("rerank_rank"),
            }
            for chunk in chunks
        ]
