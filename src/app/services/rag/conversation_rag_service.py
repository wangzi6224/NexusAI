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
from src.app.services.rag.hybrid_retriever import HybridRetriever
from src.app.services.rag.prompt_builder import RagPromptBuilder
from src.app.services.rag.query_rewriter import QueryRewriter
from src.app.services.rag.retrieval_mode import (
    RETRIEVAL_MODE_HYBRID,
    RETRIEVAL_MODE_VECTOR_RERANK,
    RetrievalMode,
)
from src.app.services.rag.retriever import RagRetriever

NO_ANSWER = "根据当前知识库资料，无法确定。"


class ConversationRagService:
    def __init__(self) -> None:
        self.query_rewriter = QueryRewriter()
        self.retriever = RagRetriever()
        self.hybrid_retriever = HybridRetriever()
        self.prompt_builder = RagPromptBuilder()
        self.llm_provider = OllamaProvider()

    def ask(
        self,
        conversation_id: str,
        question: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        model: str | None = None,
        candidate_k: int | None = None,
        rerank_top_n: int | None = None,
        rerank_enabled: bool | None = None,
        retrieval_mode: RetrievalMode = RETRIEVAL_MODE_VECTOR_RERANK,
        vector_top_k: int = 30,
        keyword_top_k: int = 30,
        fusion_top_k: int = 20,
        enable_mmr: bool = True,
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
        if retrieval_mode == RETRIEVAL_MODE_HYBRID:
            search_result = self.hybrid_retriever.search(
                query=rewritten_query,
                vector_top_k=vector_top_k,
                keyword_top_k=keyword_top_k,
                fusion_top_k=fusion_top_k,
                final_top_k=top_k,
                score_threshold=score_threshold,
                enable_mmr=enable_mmr,
                enable_rerank=rerank_enabled if rerank_enabled is not None else True,
            )
        else:
            search_result = self.retriever.search(
                query=rewritten_query,
                top_k=top_k,
                score_threshold=score_threshold,
                candidate_k=candidate_k,
                rerank_top_n=rerank_top_n,
                rerank_enabled=rerank_enabled,
            )

        search_trace = search_result["trace"]

        retrieval_latency_ms = int((perf_counter() - retrieval_start) * 1000)

        chunks = search_result["chunks"]

        if not chunks:
            trace = {
                "original_query": clean_question,
                "rewritten_query": rewritten_query,
                "retrieval_mode": retrieval_mode,
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
                "score": float(
                    chunk.get("score")
                    or chunk.get("rerank_score")
                    or chunk.get("vector_score")
                    or 0.0
                ),
            }
            for chunk in chunks
        ]

        trace = {
            # 原始用户问题
            "original_query": clean_question,
            # 重写后用于检索的 query
            "rewritten_query": rewritten_query,
            # 检索模式：vector_rerank 或 hybrid
            "retrieval_mode": retrieval_mode,
            # 是否进行了重写
            "rewrite_changed": rewrite_result["rewrite_changed"],
            # 本次对话上下文消息数量
            "context_message_count": len(recent_messages),
            # 最终检索到并用于生成回答的 chunk 数量
            "retrieved_count": len(chunks),
            # 传入的 top_k 参数，表示希望返回的 top 结果数
            "top_k": top_k,
            # 传入的 candidate_k 参数，表示向量检索召回的候选数量
            "candidate_k": candidate_k,
            # 混合检索参数：向量召回数量
            "vector_top_k": vector_top_k,
            # 混合检索参数：关键词召回数量
            "keyword_top_k": keyword_top_k,
            # 混合检索参数：融合候选数量
            "fusion_top_k": fusion_top_k,
            # 混合检索参数：是否启用 MMR
            "enable_mmr": enable_mmr,
            # 传入的 rerank_top_n 参数，表示 rerank 后保留的结果数量
            "rerank_top_n": rerank_top_n,
            # 传入的相似度阈值
            "score_threshold": score_threshold,
            # 候选总数（不同检索模式字段不同）
            "candidate_count": search_trace.get(
                "candidate_count",
                search_trace.get("fusion_count", 0),
            ),
            # 重写耗时
            "rewrite_latency_ms": rewrite_result["latency_ms"],
            # 嵌入计算耗时
            "embedding_latency_ms": search_trace.get("embedding_latency_ms", 0),
            # 检索耗时（不同检索模式字段不同）
            "retrieval_latency_ms": search_trace.get(
                "retrieval_latency_ms",
                search_trace.get("total_retrieval_latency_ms", retrieval_latency_ms),
            ),
            # 混合检索细分耗时
            "vector_latency_ms": search_trace.get("vector_latency_ms", 0),
            "keyword_latency_ms": search_trace.get("keyword_latency_ms", 0),
            "fusion_latency_ms": search_trace.get("fusion_latency_ms", 0),
            "mmr_latency_ms": search_trace.get("mmr_latency_ms", 0),
            # rerank 耗时
            "rerank_latency_ms": search_trace.get("rerank_latency_ms", 0),
            # 生成回答耗时
            "generation_latency_ms": generation_latency_ms,
            # rerank 是否启用
            "rerank_enabled": search_trace.get("rerank_enabled", False),
            # rerank 使用的模型
            "rerank_model": search_trace.get("rerank_model"),
            # rerank 失败时的降级原因
            "rerank_fallback_reason": search_trace.get("rerank_fallback_reason"),
            # query 重写失败或没命中时的降级原因
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
