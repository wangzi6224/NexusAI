from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AssistantMode(StrEnum):
    """统一 Assistant 支持的入口模式。"""

    AUTO = "auto"
    CHAT = "chat"
    RAG = "rag"
    AGENT = "agent"


class RetrievalMode(StrEnum):
    """RAG 检索模式。"""

    VECTOR = "vector"
    VECTOR_RERANK = "vector_rerank"
    HYBRID = "hybrid"


class AssistantRunStatus(StrEnum):
    """assistant_run 生命周期状态。"""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AssistantOptions(BaseModel):
    """统一入口的可选参数。

    注意：这里不要一次性塞太多业务参数，只放 chat/rag/agent 都可能会用到的稳定参数。
    """

    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.3, ge=0, le=1)
    retrieval_mode: RetrievalMode = RetrievalMode.HYBRID
    enable_rerank: bool = True
    enable_agent: bool = True
    enable_mcp_tools: bool = False
    max_steps: int = Field(default=3, ge=1, le=8)


class AssistantStreamRequest(BaseModel):
    """统一 Assistant 流式请求。"""

    message: str = Field(..., min_length=1, description="用户当前输入")
    mode: AssistantMode = AssistantMode.AUTO
    model: str | None = None
    options: AssistantOptions = Field(default_factory=AssistantOptions)


class AssistantEventType(StrEnum):
    """统一 SSE 事件类型。"""

    ASSISTANT_START = "assistant_start"
    ROUTE_DECISION = "route_decision"
    REWRITE = "rewrite"
    RETRIEVAL_START = "retrieval_start"
    SOURCE = "source"
    TOOL_CALL_START = "tool_call_start"
    TOOL_CALL_END = "tool_call_end"
    DELTA = "delta"
    ASSISTANT_END = "assistant_end"
    ERROR = "error"
    DONE = "done"


class AssistantStreamEvent(BaseModel):
    """统一 SSE 事件对象。

    event 是事件名，data 是事件负载。
    """

    event: AssistantEventType
    data: dict[str, Any] = Field(default_factory=dict)


class RouteDecision(BaseModel):
    """mode=auto 时的路由结果。"""

    requested_mode: AssistantMode
    resolved_mode: AssistantMode
    reason: str
    confidence: float = Field(default=1.0, ge=0, le=1)


class AssistantRunCreate(BaseModel):
    id: str
    conversation_id: str
    input: str
    mode: AssistantMode
    model: str | None = None
    provider: str | None = None
    trace: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssistantRunUpdate(BaseModel):
    status: AssistantRunStatus
    user_message_id: str | None = None
    assistant_message_id: str | None = None
    final_answer: str | None = None
    model: str | None = None
    provider: str | None = None
    latency_ms: int | None = None
    trace: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
