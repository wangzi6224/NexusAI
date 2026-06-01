from typing import Literal

from pydantic import BaseModel, Field
from src.app.services.assistant.mode import ResolvedAssistantMode

RouteSource = Literal["rule", "llm", "fallback"]


class RouteDecision(BaseModel):
    """
    智能路由决策结果模型。
    - mode: 最终路由模式，必选项。
    - confidence: 主要是看路由选择可信程度，默认为 1.0，范围 [0, 1]。
    - source: 路由来源，必选项，值为 "rule"、"llm" 或 "fallback"。
    - reason: 可审计的路由原因，必选项，长度限制 [1, 300]。
    - should_rewrite_query: 是否需要重写用户查询，默认为 False。
    - retrieval_mode: 可选项，RAG 模式下的检索模式，如 "keyword"、"dense" 等。
    - enable_rerank: 可选项，是否启用重排序功能。
    - enable_mcp_tools: 可选项，是否启用 MCP 相关工具。
    """

    mode: ResolvedAssistantMode = Field(..., description="最终路由模式")
    confidence: float = Field(default=1.0, ge=0, le=1, description="路由置信度")
    source: RouteSource = Field(..., description="路由来源：规则、LLM 或 fallback")
    reason: str = Field(..., min_length=1, max_length=300, description="可审计原因")
    matched_keywords: list[str] = Field(default_factory=list, description="命中的规则关键词")
    should_rewrite_query: bool = Field(
        default=False, description="是否需要重写用户查询"
    )
    retrieval_mode: str | None = Field(
        default=None, description="RAG 模式下的检索模式，如 'keyword'、'dense' 等"
    )
    enable_rerank: bool | None = Field(default=None, description="是否启用重排序功能")
    enable_mcp_tools: bool = Field(default=False, description="是否启用 MCP 相关工具")
