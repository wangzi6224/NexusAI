from typing import Any

from fastapi import APIRouter

from src.app.schemas.schemas import (
    EmbedAllDocumentsResponse,
    EmbedDocumentResponse,
    EmbeddingStatusResponse,
    EmbeddingTestRequest,
    EmbeddingTestResponse,
    SearchDebugRequest,
    SearchDebugResponse,
)
from src.app.services.embedding_service import get_embedding_service

router = APIRouter()


# 测试 Embedding：对一段文本生成向量，验证 embedding 服务是否可用
@router.post(
    "/embeddings/test",
    response_model=EmbeddingTestResponse,
    tags=["Embedding"],
    summary="测试 Embedding",
    description="对输入文本生成向量，用于验证 embedding 服务和模型是否正常工作。",
)
def test_embedding_api(request: EmbeddingTestRequest) -> EmbeddingTestResponse:
    result = get_embedding_service().test_embedding(request.text)
    return EmbeddingTestResponse(**result)


# 向量化单个文档：为指定文档生成并保存 embedding
@router.post(
    "/documents/{document_id}/embed",
    response_model=EmbedDocumentResponse,
    tags=["Embedding"],
    summary="向量化单个文档",
    description="对指定文档的文本分块生成 embedding，并保存向量结果。",
)
def embed_document_api(
    document_id: str,
    model_name: str | None = None,
) -> EmbedDocumentResponse:
    result = get_embedding_service().embed_document(
        document_id=document_id,
        model_name=model_name,
    )
    return EmbedDocumentResponse(**result)


# 查看文档向量状态：确认文档是否已经完成 embedding
@router.get(
    "/documents/{document_id}/embedding-status",
    response_model=EmbeddingStatusResponse,
    tags=["Embedding"],
    summary="获取文档向量状态",
    description="根据文档 ID 返回该文档的 embedding 生成状态。",
)
def get_document_embedding_status_api(
    document_id: str,
) -> EmbeddingStatusResponse:
    result = get_embedding_service().get_document_embedding_status(document_id)
    return EmbeddingStatusResponse(**result)


# 批量向量化文档：为所有未处理文档生成 embedding
@router.post(
    "/documents/embed-all",
    response_model=EmbedAllDocumentsResponse,
    tags=["Embedding"],
    summary="批量向量化文档",
    description="为所有文档批量生成 embedding，可通过 force 重新生成已有向量。",
)
def embed_all_documents_api(
    force: bool = False,
    model_name: str | None = None,
) -> EmbedAllDocumentsResponse:
    result: dict[str, Any] = get_embedding_service().embed_all_documents(
        force=force,
        model_name=model_name,
    )
    return EmbedAllDocumentsResponse(**result)


# Embedding 搜索调试：直接查看向量检索命中的文档块
@router.post(
    "/embeddings/search-debug",
    response_model=SearchDebugResponse,
    tags=["Embedding"],
    summary="Embedding 搜索调试",
    description="基于输入 query 执行向量检索，返回命中的文档分块和相似度信息。",
)
def search_debug_api(request: SearchDebugRequest) -> SearchDebugResponse:
    result: dict[str, Any] = get_embedding_service().search_debug(
        query=request.query,
        top_k=request.top_k,
    )
    return SearchDebugResponse(**result)

