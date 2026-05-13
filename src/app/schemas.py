from pydantic import BaseModel, Field
from typing import Any


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户输入的问题")
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


class ModelsResponse(BaseModel):
    current_model: str
    available_models: list[str]


class SelectModelRequest(BaseModel):
    model: str


class SelectModelResponse(BaseModel):
    success: bool
    selected_model: str
    message: str


class ConversationCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, description="会话标题")
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


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="用户本次发送的消息内容")
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
