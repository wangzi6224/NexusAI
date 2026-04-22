from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    model: str
    elapsed_seconds: float


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
