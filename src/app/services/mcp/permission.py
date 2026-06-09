# src/app/services/mcp/permission.py
from __future__ import annotations

from src.app.config import get_settings
from src.app.services.mcp.schemas import McpToolSpec


class McpPermission:
    """MCP 工具权限控制。

    第一版只做 allowlist。
    Week 26 再升级到 user/workspace/tool scope。
    """

    def allowed_tools(self) -> set[str]:
        raw = getattr(get_settings(), "mcp_allowed_tools", "")
        return {item.strip() for item in raw.split(",") if item.strip()}

    def validate_tool(self, tool: McpToolSpec) -> None:
        allowed = self.allowed_tools()

        if tool.full_name not in allowed:
            raise PermissionError(f"MCP 工具不在白名单中: {tool.full_name}")

        if tool.risk_level == "high":
            raise PermissionError(f"高风险 MCP 工具当前禁止自动执行: {tool.full_name}")
