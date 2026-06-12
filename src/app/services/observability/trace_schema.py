from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field

SpanStatus = Literal["running", "success", "error", "cancelled"]

SpanType = Literal[
    "assistant.run",
    "router.decision",
    "memory.short_term.load",
    "memory.long_term.retrieve",
    "memory.long_term.write",
    "working_memory.update",
    "context.assemble",
    "context.final_assemble",
    "context.compress",
    "agent.run",
    "planner.decision",
    "planner.fallback",
    "tool.call",
    "mcp.call",
    "llm.call",
    "security.check",
    "eval.judge",
]


class TokenUsage(BaseModel):
    """一次模型调用的 token 使用情况。"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class CostUsage(BaseModel):
    """一次模型调用的成本估算。"""

    currency: str = "USD"
    prompt_cost: float = 0
    completion_cost: float = 0
    total_cost: float = 0
    estimated: bool = True


class TraceSpanCreate(BaseModel):
    """创建 span 的请求模型。"""

    trace_id: str
    parent_span_id: str | None = None
    run_id: str
    conversation_id: str | None = None
    assistant_run_id: str | None = None
    agent_run_id: str | None = None
    span_type: SpanType
    name: str
    input: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TraceSpan(BaseModel):
    """统一 LLMOps Span。"""

    id: str
    trace_id: str
    parent_span_id: str | None = None
    run_id: str
    conversation_id: str | None = None
    assistant_run_id: str | None = None
    agent_run_id: str | None = None
    span_type: SpanType
    name: str
    status: SpanStatus
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    error_code: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    latency_ms: int | None = None
    started_at: str | None = None
    ended_at: str | None = None


class TraceTree(BaseModel):
    """前端 Trace Drawer 使用的树结构。"""

    trace_id: str
    spans: list[TraceSpan]
    summary: dict[str, Any] = Field(default_factory=dict)
