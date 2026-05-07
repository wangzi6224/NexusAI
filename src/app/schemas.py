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
