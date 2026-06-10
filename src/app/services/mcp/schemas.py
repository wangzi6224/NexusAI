from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator

# 风险等级枚举，表示 MCP 工具的潜在风险程度。
McpRiskLevel = Literal["low", "medium", "high"]

# 传输类型枚举，表示 MCP Server 与系统的通信方式。
McpTransportType = Literal["stdio", "SSE/HTTP", "Streaming HTTP"]


class McpServerConfig(BaseModel):
    """外部 MCP Server 运行配置。"""

    id: str | None = None
    name: str = Field(min_length=1)
    transport: McpTransportType = "stdio"
    command: str = Field(min_length=1)
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    enabled: bool = True
    timeout_seconds: int = Field(default=15, ge=1, le=120)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("MCP server name 不能为空")

        if "__" in normalized:
            raise ValueError("MCP server name 不能包含连续双下划线")

        return normalized


class McpServerCreate(BaseModel):
    """动态注册外部 MCP Server 的请求。"""

    name: str = Field(min_length=1)
    transport: McpTransportType = "stdio"
    command: str = Field(min_length=1)
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    enabled: bool = True
    timeout_seconds: int = Field(default=15, ge=1, le=120)
    metadata: dict[str, Any] = Field(default_factory=dict)


class McpServerUpdate(BaseModel):
    """更新外部 MCP Server 配置。未传字段保持不变。"""

    command: str | None = None
    args: list[str] | None = None
    env: dict[str, str] | None = None
    enabled: bool | None = None
    timeout_seconds: int | None = Field(default=None, ge=1, le=120)
    metadata: dict[str, Any] | None = None


class McpToolSpec(BaseModel):
    """外部 MCP 工具描述。"""

    id: str | None = None
    server_name: str
    tool_name: str
    full_name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)
    risk_level: McpRiskLevel = "low"
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class McpToolCreate(BaseModel):
    """动态注册外部 MCP Tool 的请求。"""

    tool_name: str = Field(min_length=1)
    full_name: str | None = None
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)
    risk_level: McpRiskLevel = "low"
    enabled: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class McpToolUpdate(BaseModel):
    """更新外部 MCP Tool 配置。未传字段保持不变。"""

    description: str | None = None
    input_schema: dict[str, Any] | None = None
    risk_level: McpRiskLevel | None = None
    enabled: bool | None = None
    metadata: dict[str, Any] | None = None


class McpToolCallRequest(BaseModel):
    """调试调用外部 MCP Tool 的请求。"""

    arguments: dict[str, Any] = Field(default_factory=dict)


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
