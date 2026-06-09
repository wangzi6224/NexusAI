from __future__ import annotations

from typing import Any

from src.app.config import get_settings
from src.app.services.mcp.audit_store import McpAuditStore
from src.app.services.mcp.client import McpClient
from src.app.services.mcp.permission import McpPermission
from src.app.services.mcp.schemas import McpServerConfig, McpToolSpec
from src.app.services.tools.base import Tool
from src.app.services.tools.result import tool_error, tool_success


class McpToolAdapter(Tool):
    """把外部 MCP Tool 适配成 NexusAI 内部 Tool。"""

    def __init__(
        self,
        *,
        server: McpServerConfig,
        spec: McpToolSpec,
        client: McpClient | None = None,
        permission: McpPermission | None = None,
        audit_store: McpAuditStore | None = None,
    ) -> None:
        self.server = server
        self.spec = spec
        self.client = client or McpClient()
        self.permission = permission or McpPermission()
        self.audit_store = audit_store or McpAuditStore()

        self.name = spec.full_name
        self.description = f"[MCP:{spec.server_name}] {spec.description}"
        self.parameters = spec.input_schema or {"type": "object", "properties": {}}
        self.source = "mcp"
        self.risk_level = spec.risk_level

    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            self.permission.validate_tool(self.spec)
        except PermissionError as exc:
            return tool_error(
                tool_name=self.name,
                code="MCP_PERMISSION_DENIED",
                message=str(exc),
                metadata={
                    "source": "mcp",
                    "server_name": self.spec.server_name,
                    "tool_name": self.spec.tool_name,
                    "risk_level": self.spec.risk_level,
                },
            )

        result = self.client.call_tool(
            server=self.server,
            tool_name=self.spec.tool_name,
            full_name=self.spec.full_name,
            arguments=arguments,
        )

        max_chars = getattr(get_settings(), "mcp_max_result_chars", 8000)
        content = result.content[:max_chars]
        truncated = len(result.content) > max_chars

        self.audit_store.create_log(
            result=result,
            arguments=arguments,
            risk_level=self.spec.risk_level,
            metadata={"truncated": truncated},
        )

        if not result.success:
            return tool_error(
                tool_name=self.name,
                code=result.error_code or "MCP_TOOL_CALL_FAILED",
                message=result.error_message or "MCP 工具调用失败",
                latency_ms=result.latency_ms,
                metadata={
                    "source": "mcp",
                    "server_name": self.spec.server_name,
                    "tool_name": self.spec.tool_name,
                    "risk_level": self.spec.risk_level,
                },
            )

        return tool_success(
            tool_name=self.name,
            data={
                "content": content,
                "truncated": truncated,
                "server_name": self.spec.server_name,
                "tool_name": self.spec.tool_name,
            },
            latency_ms=result.latency_ms,
            metadata={
                "source": "mcp",
                "server_name": self.spec.server_name,
                "tool_name": self.spec.tool_name,
                "full_tool_name": self.spec.full_name,
                "risk_level": self.spec.risk_level,
                "truncated": truncated,
            },
        )
