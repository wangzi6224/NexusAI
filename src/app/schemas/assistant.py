from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from src.app.services.assistant.mode import AssistantMode, ResolvedAssistantMode


class AssistantOptions(BaseModel):
    """统一 Assistant 入口的可选参数。

    注意：这里不再出现 retrieval_mode 作为顶层 routing 参数。
    因为 RAG 已经通过 tools 被 Agent 使用。
    """

    top_k: int = Field(default=5, ge=1, le=20)
    score_threshold: float = Field(default=0.3, ge=0, le=1)
    max_steps: int = Field(default=3, ge=1, le=8)

    # 预留开关：当前主要用于 auto 路由和后续 MCP。
    enable_tools: bool = True
    enable_rag_tools: bool = True
    enable_mcp_tools: bool = False


class AssistantStreamRequest(BaseModel):
    message: str = Field(..., min_length=1, description="用户当前输入")
    mode: AssistantMode = Field(
        default="auto", description="chat / agent / rag / mcp / auto"
    )
    model: str | None = None
    provider: str | None = None
    options: AssistantOptions = Field(default_factory=AssistantOptions)


class RouteDecision(BaseModel):
    mode: ResolvedAssistantMode
    reason: str
    matched_keywords: list[str] = Field(default_factory=list)


class AssistantRunCreate(BaseModel):
    conversation_id: str
    mode: ResolvedAssistantMode | AssistantMode
    input: str
    model: str | None = None
    provider: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
