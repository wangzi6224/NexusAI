from typing import Any
from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    step: int
    type: str
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: dict[str, Any] | None = None
    success: bool = True
    latency_ms: int = 0
    reason: str | None = None


class AgentState(BaseModel):
    conversation_id: str
    user_message_id: str
    question: str
    messages: list[dict[str, Any]]
    steps: list[AgentStep] = Field(default_factory=list)
    max_steps: int = 3
    model: str
    top_k: int = 5
    score_threshold: float = 0.3
