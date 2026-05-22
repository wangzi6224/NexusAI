from time import perf_counter
from typing import Any

from src.app.config import get_ollama_model
from src.app.conversation_store import (
    create_message,
    get_conversation,
    list_messages,
    update_conversation,
)
from src.app.exceptions import ConversationError
from src.app.services.llm.ollama_provider import OllamaProvider
from src.app.services.rag.prompt_builder import RagPromptBuilder
from src.app.services.rag.query_rewriter import QueryRewriter
from src.app.services.rag.retriever import RagRetriever

NO_ANSWER = "根据当前知识库资料，无法确定。"


class ConversationRagService:
    def __init__(self) -> None:
        self.query_rewriter = QueryRewriter()
        self.retriever = RagRetriever()
        self.prompt_builder = RagPromptBuilder()
        self.llm_provider = OllamaProvider()

    def ask(
        self,
        conversation_id: str,
        question: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        model: str | None = None,
    ) -> dict[str, Any]:
        conversation = get_conversation(conversation_id)

        if conversation is None:
            raise ConversationError(
                message="会话不存在",
                detail=f"conversation_id={conversation_id}",
                status_code=404,
            )

        # 清理用户输入的问题，去除首尾空白字符，并检查是否为空
        clean_question = question.strip()

        if not clean_question:
            raise ConversationError(
                message="问题不能为空",
                status_code=400,
            )

        selected_model = model or conversation.get("model") or get_ollama_model()

        user_message = create_message(
            conversation_id=conversation_id,
            role="user",
            content=clean_question,
            metadata={
                "type": "conversation_rag_user_question",
            },
        )

        recent_messages = list_messages(conversation_id)[-10:]

        rewrite_result = self.query_rewriter.rewrite(
            conversation_summary=conversation.get("summary"),
            recent_messages=recent_messages,
            current_question=clean_question,
            model=selected_model,
        )

        rewritten_query = rewrite_result["rewritten_query"]

        retrieval_start = perf_counter()
        search_result = self.retriever.search(
            query=rewritten_query,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        retrieval_latency_ms = int((perf_counter() - retrieval_start) * 1000)

        chunks = search_result["chunks"]

        if not chunks:
            trace = {
                "original_query": clean_question,
                "rewritten_query": rewritten_query,
                "rewrite_changed": rewrite_result["rewrite_changed"],
                "context_message_count": len(recent_messages),
                "retrieved_count": 0,
                "top_k": top_k,
                "score_threshold": score_threshold,
                "rewrite_latency_ms": rewrite_result["latency_ms"],
                "retrieval_latency_ms": retrieval_latency_ms,
                "generation_latency_ms": 0,
                "fallback_reason": rewrite_result.get("fallback_reason"),
            }

            assistant_message = create_message(
                conversation_id=conversation_id,
                role="assistant",
                content=NO_ANSWER,
                metadata={
                    "type": "conversation_rag_answer",
                    "user_message_id": user_message["id"],
                    "original_query": clean_question,
                    "rewritten_query": rewritten_query,
                    "sources": [],
                    "trace": trace,
                },
            )

            update_conversation(conversation_id, {})

            return {
                "conversation_id": conversation_id,
                "question": clean_question,
                "rewritten_query": rewritten_query,
                "answer": assistant_message["content"],
                "sources": [],
                "trace": trace,
            }

        messages = self.prompt_builder.build(
            question=clean_question,
            chunks=chunks,
        )

        generation_start = perf_counter()
        response = self.llm_provider.chat(
            messages=messages,
            model=selected_model,
        )
        generation_latency_ms = int((perf_counter() - generation_start) * 1000)

        sources = [
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "heading": chunk.get("heading"),
                "chunk_index": chunk["chunk_index"],
                "score": chunk["score"],
            }
            for chunk in chunks
        ]

        trace = {
            "original_query": clean_question,
            "rewritten_query": rewritten_query,
            "rewrite_changed": rewrite_result["rewrite_changed"],
            "context_message_count": len(recent_messages),
            "retrieved_count": len(chunks),
            "top_k": top_k,
            "score_threshold": score_threshold,
            "rewrite_latency_ms": rewrite_result["latency_ms"],
            "retrieval_latency_ms": retrieval_latency_ms,
            "generation_latency_ms": generation_latency_ms,
            "fallback_reason": rewrite_result.get("fallback_reason"),
        }

        assistant_message = create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response.content,
            metadata={
                "type": "conversation_rag_answer",
                "user_message_id": user_message["id"],
                "model": response.model,
                "provider": response.provider,
                "original_query": clean_question,
                "rewritten_query": rewritten_query,
                "sources": sources,
                "trace": trace,
            },
        )

        update_conversation(conversation_id, {})

        return {
            "conversation_id": conversation_id,
            "question": clean_question,
            "rewritten_query": rewritten_query,
            "answer": assistant_message["content"],
            "sources": sources,
            "trace": trace,
        }
