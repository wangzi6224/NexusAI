from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, Query
from fastapi.responses import FileResponse, StreamingResponse

from src.app.paths import STATIC_DIR
from src.app.schemas.schemas import (
    ChatRequest,
    HistoryItem,
    ChatResponse,
    HealthResponse,
    ModelsResponse,
    SelectModelRequest,
    SelectModelResponse,
    ClearHistoryResponse,
    ConversationCreateRequest,
    ConversationDetailResponse,
    ConversationItem,
    ConversationListResponse,
    MessageItem,
    MessageListResponse,
    SendMessageRequest,
    SendMessageResponse,
    ContextPreviewResponse,
    SummaryUpdateResponse,
    DocumentChunkItem,
    DocumentChunkListResponse,
    DocumentDetailResponse,
    DocumentItem,
    DocumentListResponse,
    UploadDocumentResponse,
    DeleteDocumentResponse,
    EmbeddingTestRequest,
    EmbeddingTestResponse,
    EmbedDocumentResponse,
    EmbedAllDocumentsResponse,
    EmbeddingStatusResponse,
    SearchDebugRequest,
    SearchDebugResponse,
    RagSearchRequest,
    RagSearchResponse,
    RagAskRequest,
    RagAskResponse,
    ConversationRagAskRequest,
    ConversationRagAskResponse,
    RagSearchDebugResponse,
)
from src.app.services.rag.rag_service import RagService
from src.app.services.model_service import get_models, select_model
from src.app.services.history_service import clear_chat_history, get_history
from src.app.services.chat_service import handle_chat, handle_chat_stream
from src.app.services.health_service import get_health_status
from src.app.services.conversation_service import (
    create_new_conversation,
    get_conversation_detail,
    get_conversation_list,
    get_conversation_messages,
    send_conversation_message,
    stream_conversation_message,
    update_summary_manually,
    get_context_preview,
)
from src.app.services.document_service import DocumentService
from src.app.services.embedding_service import get_embedding_service
from src.app.services.rag.conversation_rag_service import ConversationRagService
from src.app.services.rag.rag_debug_service import RagDebugService

router = APIRouter()


# ===== 基础与系统状态 =====


# 首页路由：返回静态前端页面（index.html）
@router.get(
    "/",
    tags=["基础"],
    summary="返回首页",
    description="返回静态前端页面 index.html，用于打开本地 Web 界面。",
)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# 健康检查接口：返回服务状态信息
@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["基础"],
    summary="健康检查",
    description="检查后端服务是否可用，并返回当前服务状态信息。",
)
def health_check() -> HealthResponse:
    return get_health_status()


# ===== 单轮聊天 =====


# 聊天接口（同步）：接收用户消息并返回模型的完整响应
@router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["聊天"],
    summary="同步聊天",
    description="接收一条用户消息，调用当前模型生成完整回复后一次性返回。",
)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return handle_chat(message=request.message, model=request.model)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"模型调用失败: {exc}") from exc


# 聊天接口（流式）：以 Server-Sent Events 流式返回增量模型输出
@router.post(
    "/chat/stream",
    tags=["聊天"],
    summary="流式聊天",
    description="接收一条用户消息，通过 Server-Sent Events 持续返回模型增量输出。",
)
def chat_stream(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        handle_chat_stream(
            message=request.message,
            model=request.model,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ===== 历史记录与模型管理 =====


# 获取聊天记录：返回历史聊天条目列表
@router.get(
    "/history",
    response_model=list[HistoryItem],
    tags=["历史与模型"],
    summary="获取聊天记录",
    description="读取并返回普通聊天接口保存的历史消息列表。",
)
def get_chat_history() -> list[HistoryItem]:
    records = get_history()
    return [HistoryItem(**record) for record in records]


# 清空聊天记录：删除所有历史会话/消息
@router.post(
    "/history/clear",
    response_model=ClearHistoryResponse,
    tags=["历史与模型"],
    summary="清空聊天记录",
    description="删除普通聊天接口保存的全部历史消息。",
)
def clear_history() -> ClearHistoryResponse:
    try:
        clear_chat_history()
        return ClearHistoryResponse(success=True, message="聊天记录已清空")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"清空聊天记录失败: {exc}") from exc


# 列出可用模型：返回当前支持的模型信息
@router.get(
    "/models",
    response_model=ModelsResponse,
    tags=["历史与模型"],
    summary="列出可用模型",
    description="返回当前后端可用的模型列表，以及当前选中的模型信息。",
)
def models() -> ModelsResponse:
    return get_models()


# 选择模型接口：设置/切换使用的模型
@router.post(
    "/model/select",
    response_model=SelectModelResponse,
    tags=["历史与模型"],
    summary="选择模型",
    description="切换当前使用的模型，后续聊天请求默认使用该模型。",
)
def select_model_api(request: SelectModelRequest) -> SelectModelResponse:
    try:
        return select_model(request.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ===== 会话管理 =====


# 创建会话：新建一个会话并返回会话详情
@router.post(
    "/conversations",
    response_model=ConversationDetailResponse,
    tags=["会话"],
    summary="创建会话",
    description="创建一个新的多轮会话，可指定标题和模型。",
)
def create_conversation_api(
    request: ConversationCreateRequest,
) -> ConversationDetailResponse:
    conversation = create_new_conversation(
        title=request.title,
        model=request.model,
    )
    return ConversationDetailResponse(
        **conversation,
        message_count=0,
    )


# 列出会话：返回所有会话的摘要列表
@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    tags=["会话"],
    summary="列出会话",
    description="返回所有多轮会话的摘要列表，用于会话侧边栏或列表页展示。",
)
def list_conversations_api() -> ConversationListResponse:
    conversations = get_conversation_list()
    return ConversationListResponse(
        items=[ConversationItem(**item) for item in conversations]
    )


# 获取会话详情：根据 conversation_id 返回会话完整信息
@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    tags=["会话"],
    summary="获取会话详情",
    description="根据会话 ID 返回单个会话的完整信息。",
)
def get_conversation_api(
    conversation_id: str,
) -> ConversationDetailResponse:
    conversation = get_conversation_detail(conversation_id)
    return ConversationDetailResponse(**conversation)


# 列出会话消息：返回指定会话的消息列表
@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessageListResponse,
    tags=["会话"],
    summary="列出会话消息",
    description="根据会话 ID 返回该会话下的全部消息列表。",
)
def list_conversation_messages_api(
    conversation_id: str,
) -> MessageListResponse:
    messages = get_conversation_messages(conversation_id)
    return MessageListResponse(items=[MessageItem(**item) for item in messages])


# 发送会话消息：向指定会话发送用户消息并返回用户/助手消息对象
@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
    tags=["会话"],
    summary="发送会话消息",
    description="向指定会话追加用户消息，并返回用户消息和助手回复消息。",
)
def send_conversation_message_api(
    conversation_id: str,
    request: SendMessageRequest,
) -> SendMessageResponse:
    result = send_conversation_message(
        conversation_id=conversation_id,
        content=request.content,
        model=request.model,
    )

    return SendMessageResponse(
        user_message=MessageItem(**result["user_message"]),
        assistant_message=MessageItem(**result["assistant_message"]),
    )


# 发送会话消息，以 Server-Sent Events 流式返回增量模型输出
@router.post(
    "/conversations/{conversation_id}/messages/stream",
    tags=["会话"],
    summary="流式发送会话消息",
    description="向指定会话追加用户消息，并通过 Server-Sent Events 流式返回助手回复。",
)
def stream_conversation_message_api(
    conversation_id: str,
    request: SendMessageRequest,
) -> StreamingResponse:
    return StreamingResponse(
        stream_conversation_message(
            conversation_id=conversation_id,
            content=request.content,
            model=request.model,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# 预览会话上下文：查看实际发给模型前的上下文内容
@router.get(
    "/conversations/{conversation_id}/context-preview",
    response_model=ContextPreviewResponse,
    tags=["会话"],
    summary="预览会话上下文",
    description="查看指定会话组装给模型前的上下文内容，便于调试多轮上下文。",
)
def get_context_preview_api(
    conversation_id: str,
) -> ContextPreviewResponse:
    preview_data: dict[str, Any] = get_context_preview(conversation_id)
    return ContextPreviewResponse(**preview_data)


# 更新会话摘要：手动触发长会话摘要刷新
@router.post(
    "/conversations/{conversation_id}/summary",
    response_model=SummaryUpdateResponse,
    tags=["会话"],
    summary="更新会话摘要",
    description="手动触发指定会话的摘要更新，用于压缩和维护长对话上下文。",
)
def update_conversation_summary_api(
    conversation_id: str,
) -> SummaryUpdateResponse:
    result: dict[str, Any] = update_summary_manually(conversation_id)
    return SummaryUpdateResponse(**result)


# ===== 文档管理 =====


# 上传文档：保存文件并提取可用于后续检索和向量化的文本内容
@router.post(
    "/documents/upload",
    response_model=UploadDocumentResponse,
    tags=["文档"],
    summary="上传文档",
    description="上传本地文件，保存文档元信息并提取文本内容。",
)
async def upload_document_api(
    file: UploadFile = File(...),
) -> UploadDocumentResponse:
    result = await DocumentService().upload_document(file)
    return UploadDocumentResponse(**result)


# 列出文档：返回已上传文档的摘要列表
@router.get(
    "/documents",
    response_model=DocumentListResponse,
    tags=["文档"],
    summary="列出文档",
    description="返回当前系统中已经上传的文档列表。",
)
def list_documents_api() -> DocumentListResponse:
    documents = DocumentService().list_documents()
    return DocumentListResponse(items=[DocumentItem(**item) for item in documents])


# 获取文档详情：查看单个文档的元信息和处理状态
@router.get(
    "/documents/{document_id}",
    response_model=DocumentDetailResponse,
    tags=["文档"],
    summary="获取文档详情",
    description="根据文档 ID 返回该文档的详细信息。",
)
def get_document_api(document_id: str) -> DocumentDetailResponse:
    document = DocumentService().get_document_detail(document_id)
    return DocumentDetailResponse(**document)


# 列出文档分块：查看文档被切分后的 chunk 内容
@router.get(
    "/documents/{document_id}/chunks",
    response_model=DocumentChunkListResponse,
    tags=["文档"],
    summary="列出文档分块",
    description="根据文档 ID 返回该文档切分后的文本块列表。",
)
def list_document_chunks_api(document_id: str) -> DocumentChunkListResponse:
    chunks = DocumentService().get_document_chunks(document_id)
    return DocumentChunkListResponse(
        items=[DocumentChunkItem(**item) for item in chunks]
    )


# 删除文档：移除文档及其关联数据
@router.delete(
    "/documents/{document_id}",
    response_model=DeleteDocumentResponse,
    tags=["文档"],
    summary="删除文档",
    description="根据文档 ID 删除文档及其关联的处理结果。",
)
def delete_document_api(document_id: str) -> DeleteDocumentResponse:
    result = DocumentService().delete_document(document_id)
    return DeleteDocumentResponse(**result)


# ===== Embedding 与向量检索调试 =====


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


# ===== RAG 检索与问答 =====


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
