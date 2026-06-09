from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class McpServerConfig(BaseModel):
    """外部 MCP Server 配置。"""

    name: str = Field(min_length=1)
    command: str = Field(min_length=1)
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    enabled: bool = True
    timeout_seconds: int = Field(default=15, ge=1, le=120)


class McpToolSpec(BaseModel):
    """外部 MCP 工具描述。"""

    server_name: str
    tool_name: str
    full_name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    risk_level: Literal["low", "medium", "high"] = "low"


class McpToolCallResult(BaseModel):
    """MCP 工具调用结果。"""

    server_name: str
    tool_name: str
    full_name: str
    success: bool
    content: str = ""
    raw_result: Any | None = None
    error_code: str | None = None
    error_message: str | None = None
    latency_ms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
