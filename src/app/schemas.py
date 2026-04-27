from pydantic import BaseModel, Field


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
