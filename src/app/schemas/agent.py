from typing import Any
from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户当前问题")
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.3, ge=0, le=1)
    max_steps: int = Field(default=3, ge=1, le=8)
    model: str | None = None


class AgentChatResponse(BaseModel):
    conversation_id: str
    question: str
    answer: str
    tool_calls: list[dict[str, Any]]
    trace: dict[str, Any]
