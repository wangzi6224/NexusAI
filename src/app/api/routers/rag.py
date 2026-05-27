from fastapi import APIRouter, Query

from src.app.schemas.schemas import (
    ConversationRagAskRequest,
    ConversationRagAskResponse,
    RagAskRequest,
    RagAskResponse,
    RagSearchDebugResponse,
    RagSearchRequest,
    RagSearchResponse,
)
from src.app.services.rag.conversation_rag_service import ConversationRagService
from src.app.services.rag.rag_debug_service import RagDebugService
from src.app.services.rag.rag_service import RagService

router = APIRouter()


# RAG 检索调试：只返回检索结果，不生成回答，主要给前端或调试流程使用
@router.post(
    "/rag/search",
    response_model=RagSearchResponse,
    tags=["RAG"],
    summary="RAG 检索",
    description=(
        "执行 RAG 检索并直接返回检索结果，不调用模型生成回答。"
        "常用于前端调试检索参数。"
    ),
)
def rag_search_api(request: RagSearchRequest) -> RagSearchResponse:
    result = RagService().search(
        query=request.query,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        candidate_k=request.candidate_k,
        rerank_top_n=request.rerank_top_n,
        rerank_enabled=request.rerank_enabled,
        vector_top_k=request.vector_top_k,
        keyword_top_k=request.keyword_top_k,
        fusion_top_k=request.fusion_top_k,
        enable_mmr=request.enable_mmr,
        retrieval_mode=request.retrieval_mode,
    )

    return RagSearchResponse(**result)


# RAG 问答：基于文档检索结果生成回答，不绑定会话历史
@router.post(
    "/rag/ask",
    response_model=RagAskResponse,
    tags=["RAG"],
    summary="RAG 问答",
    description="先检索相关文档块，再调用模型生成回答；该接口不绑定会话历史。",
)
def rag_ask_api(request: RagAskRequest) -> RagAskResponse:
    result = RagService().ask(
        question=request.question,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        model=request.model,
        candidate_k=request.candidate_k,
        rerank_top_n=request.rerank_top_n,
        rerank_enabled=request.rerank_enabled,
    )
    return RagAskResponse(**result)


# 会话 RAG 问答：结合会话上下文和文档检索结果生成回答
@router.post(
    "/conversations/{conversation_id}/rag/ask",
    response_model=ConversationRagAskResponse,
    tags=["RAG"],
    summary="会话 RAG 问答",
    description="在指定会话中执行 RAG 问答，结合会话上下文和文档检索结果生成回复。",
)
def conversation_rag_ask_api(
    conversation_id: str,
    request: ConversationRagAskRequest,
) -> ConversationRagAskResponse:
    result = ConversationRagService().ask(
        conversation_id=conversation_id,
        question=request.question,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        model=request.model,
        candidate_k=request.candidate_k,
        rerank_top_n=request.rerank_top_n,
        rerank_enabled=request.rerank_enabled,
        retrieval_mode=request.retrieval_mode,
        vector_top_k=request.vector_top_k,
        keyword_top_k=request.keyword_top_k,
        fusion_top_k=request.fusion_top_k,
        enable_mmr=request.enable_mmr,
    )
    return ConversationRagAskResponse(**result)


# RAG 检索对比调试：比较向量检索和混合检索的结果与性能差异
@router.get(
    "/rag/search-debug",
    response_model=RagSearchDebugResponse,
    tags=["RAG"],
    summary="RAG 检索对比调试",
    description="比较向量检索和混合检索两种模式的命中结果与性能差异。",
)
def rag_search_debug_api(
    query: str = Query(..., min_length=1, description="要比较的查询内容"),
) -> RagSearchDebugResponse:
    result = RagDebugService().compare_search(query=query)
    return RagSearchDebugResponse(**result)

