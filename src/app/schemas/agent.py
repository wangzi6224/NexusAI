from typing import Any
from pydantic import BaseModel, Field


class AgentChatRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1, description="会话ID")
    question: str = Field(..., min_length=1, description="用户当前问题")
    model: str = Field(..., description="可选，指定使用的模型名称，例如：gemma4:e2b")
    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.3, ge=0, le=1)
    max_steps: int = Field(default=15, ge=1, le=20)


class AgentChatResponse(BaseModel):
    run_id: str
    conversation_id: str
    question: str
    answer: str
    tool_calls: list[dict[str, Any]]
    trace: dict[str, Any]


class AgentRunDetailResponse(BaseModel):
    run: dict[str, Any]
    steps: list[dict[str, Any]]
    events: list[dict[str, Any]]
