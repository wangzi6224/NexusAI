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
