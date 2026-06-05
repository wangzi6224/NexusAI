from pydantic import BaseModel, Field
from typing import Any

from src.app.services.rag.retrieval_mode import (
    RETRIEVAL_MODE_VECTOR_RERANK,
    RetrievalMode,
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户输入的问题")
    provider: str | None = Field(default=None, description="可选，指定本次请求使用的 Provider")
    model: str | None = Field(default=None, description="可选，指定本次请求使用的模型")


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    answer: str
    provider: str
    model: str
    latency_ms: int
    usage: TokenUsage = Field(default_factory=TokenUsage)


class HealthResponse(BaseModel):
    ok: bool
    message: str


class HistoryItem(BaseModel):
    timestamp: str
    model: str
    user_input: str
    prompt: str
    answer: str
    elapsed_seconds: float


class ClearHistoryResponse(BaseModel):
    success: bool
    message: str


class ProviderModels(BaseModel):
    provider: str
    current_model: str
    available_models: list[str]


class CloudProviderModels(BaseModel):
    provider: str
    current_model: str
    available_models: list[str]


class ModelsResponse(BaseModel):
    current_provider: str
    current_cloud_provider: str | None = None
    current_model: str
    available_models: list[str]
    providers: list[ProviderModels] = Field(default_factory=list)
    cloud_providers: list[CloudProviderModels] = Field(default_factory=list)


class SelectModelRequest(BaseModel):
    provider: str | None = None
    cloud_provider: str | None = None
    model: str


class SelectModelResponse(BaseModel):
    success: bool
    selected_provider: str
    selected_cloud_provider: str | None = None
    selected_model: str
    message: str


class ConversationCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, description="会话标题")
    provider: str | None = Field(
        default=None, description="可选，指定该会话默认使用的 Provider"
    )
    model: str | None = Field(
        default=None, description="可选，指定该会话默认使用的模型"
    )


class ConversationItem(BaseModel):
    id: str
    title: str
    summary: str | None = None
    model: str
    provider: str
    status: str
    message_count: int = 0
    summarized_message_count: int = 0
    summary_updated_at: str | None = None
    created_at: str
    updated_at: str


class ConversationListResponse(BaseModel):
    items: list[ConversationItem]


class ConversationDetailResponse(ConversationItem):
    pass


class DeleteConversationResponse(BaseModel):
    success: bool
    message: str
    conversation_id: str


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="用户本次发送的消息内容")
    provider: str | None = Field(default=None, description="可选，覆盖本次请求使用的 Provider")
    model: str | None = Field(default=None, description="可选，覆盖本次请求使用的模型")


class MessageItem(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class MessageListResponse(BaseModel):
    items: list[MessageItem]


class SendMessageResponse(BaseModel):
    user_message: MessageItem
    assistant_message: MessageItem


class ContextMessageItem(BaseModel):
    role: str = Field(..., description="消息角色，例如 system/user/assistant/tool")
    content: str = Field(..., description="消息内容")


class ContextPreviewResponse(BaseModel):
    conversation_id: str = Field(..., description="会话 ID")
    summary: str | None = Field(default=None, description="当前会话摘要")
    recent_message_count: int = Field(..., description="进入上下文的最近消息数量")
    estimated_tokens: int = Field(..., description="粗略估算 token 数")
    estimated_chars: int = Field(..., description="上下文总字符数")
    max_recent_messages: int = Field(..., description="最多保留最近多少条消息")
    max_context_chars: int = Field(..., description="上下文最大字符数限制")
    messages: list[ContextMessageItem] = Field(
        default_factory=list,
        description="本次实际会传给 LLM 的 messages",
    )


class SummaryUpdateResponse(BaseModel):
    conversation_id: str = Field(..., description="会话 ID")
    summary: str = Field(..., description="更新后的会话摘要")
    summarized_message_count: int = Field(
        ..., description="摘要更新时会话已有的消息总数"
    )
    updated_at: str = Field(..., description="摘要更新时间")


class DocumentItem(BaseModel):
    id: str
    filename: str
    file_type: str
    source_path: str
    status: str
    chunk_count: int
    char_count: int
    error_message: str | None = None
    created_at: str
    updated_at: str


class DocumentDetailResponse(DocumentItem):
    content: str


class DocumentListResponse(BaseModel):
    items: list[DocumentItem]


class UploadDocumentResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    status: str
    chunk_count: int
    char_count: int
    created_at: str


class DocumentChunkItem(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    heading: str | None = None
    content: str
    char_count: int
    estimated_tokens: int
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class DocumentChunkListResponse(BaseModel):
    items: list[DocumentChunkItem]


class DeleteDocumentResponse(BaseModel):
    success: bool
    message: str


class EmbeddingTestRequest(BaseModel):
    text: str = Field(..., min_length=1)


class EmbeddingTestResponse(BaseModel):
    text: str
    embedding_model: str
    dimension: int
    vector_preview: list[float]
    vector_norm: float


class EmbedDocumentResponse(BaseModel):
    document_id: str
    total_chunks: int
    embedded_chunks: int
    failed_chunks: int
    embedding_model: str
    status: str


class EmbedAllDocumentsResponse(BaseModel):
    total_chunks: int
    embedded_chunks: int
    failed_chunks: int
    embedding_model: str
    status: str


class EmbeddingStatusItem(BaseModel):
    chunk_id: str
    chunk_index: int
    embedding_status: str
    embedding_model: str | None = None
    embedding_error: str | None = None
    embedding_updated_at: str | None = None


class EmbeddingStatusResponse(BaseModel):
    document_id: str
    items: list[EmbeddingStatusItem]


class SearchDebugRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchDebugChunkItem(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    heading: str | None = None
    content: str
    distance: float
    score: float


class SearchDebugResponse(BaseModel):
    query: str
    embedding_model: str
    top_k: int
    items: list[SearchDebugChunkItem]


class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.3, ge=0, le=1)

    retrieval_mode: RetrievalMode = Field(
        default=RETRIEVAL_MODE_VECTOR_RERANK,
        description="vector_rerank / hybrid",
    )

    candidate_k: int = Field(default=30, ge=1, le=100)
    rerank_top_n: int = Field(default=5, ge=1, le=20)
    rerank_enabled: bool = Field(default=True)

    vector_top_k: int = Field(default=30, ge=1, le=100)
    keyword_top_k: int = Field(default=30, ge=1, le=100)
    fusion_top_k: int = Field(default=20, ge=1, le=100)
    enable_mmr: bool = Field(default=True)


class RagSearchChunkItem(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    heading: str | None = None
    content: str
    score: float
    distance: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class RagSearchResponse(BaseModel):
    query: str
    embedding_model: str
    top_k: int
    score_threshold: float
    chunks: list[RagSearchChunkItem]


class RagSearchWithRerankChunkItem(RagSearchChunkItem):
    retrieval_rank: int | None = None
    rerank_rank: int | None = None
    vector_score: float | None = None
    rerank_score: float | None = None


class RagSearchWithRerankResponse(BaseModel):
    query: str
    embedding_model: str
    top_k: int
    score_threshold: float
    chunks: list[RagSearchWithRerankChunkItem]


class RagAskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.3, ge=0, le=1)

    candidate_k: int = Field(default=30, ge=1, le=100)
    rerank_top_n: int = Field(default=5, ge=1, le=20)
    rerank_enabled: bool = Field(default=True)

    model: str | None = None


class RagSourceItem(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    heading: str | None = None
    chunk_index: int
    score: float


class RagTrace(BaseModel):
    top_k: int
    score_threshold: float
    retrieved_count: int
    embedding_model: str
    chat_model: str
    provider: str
    latency_ms: int


class RagAskResponse(BaseModel):
    question: str
    answer: str
    sources: list[RagSourceItem]
    trace: RagTrace


class ConversationRagAskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户当前问题")
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.3, ge=0.0, le=1.0)
    model: str | None = Field(default=None)
    candidate_k: int = Field(default=30, ge=1, le=100)
    rerank_top_n: int = Field(default=5, ge=1, le=20)
    rerank_enabled: bool = Field(default=True)
    retrieval_mode: RetrievalMode = Field(
        default=RETRIEVAL_MODE_VECTOR_RERANK,
        description="vector_rerank / hybrid",
    )
    vector_top_k: int = Field(default=30, ge=1, le=100)
    keyword_top_k: int = Field(default=30, ge=1, le=100)
    fusion_top_k: int = Field(default=20, ge=1, le=100)
    enable_mmr: bool = Field(default=True)


class ConversationRagTrace(BaseModel):
    original_query: str
    rewritten_query: str
    retrieval_mode: RetrievalMode = RETRIEVAL_MODE_VECTOR_RERANK
    rewrite_changed: bool
    context_message_count: int
    retrieved_count: int
    top_k: int
    score_threshold: float
    rewrite_latency_ms: int
    retrieval_latency_ms: int
    generation_latency_ms: int
    fallback_reason: str | None = None


class ConversationRagAskResponse(BaseModel):
    conversation_id: str
    question: str
    rewritten_query: str
    answer: str
    sources: list[RagSourceItem]
    trace: ConversationRagTrace


class RagSearchDebugRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用于调试的查询消息")


class RagSearchDebugResponse(BaseModel):
    query: str
    without_rerank: RagSearchResponse
    with_rerank: RagSearchWithRerankResponse
    compare: list[dict[str, Any]]
    latency_ms: int
