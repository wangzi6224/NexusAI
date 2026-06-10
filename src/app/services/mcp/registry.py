from __future__ import annotations

from src.app.services.mcp.schemas import McpServerConfig, McpToolSpec
from src.app.services.mcp.store import McpStore
from src.app.services.mcp.tool_adapter import McpToolAdapter
from src.app.services.tools.registry import ToolRegistry


class McpRegistry:
    """MCP 工具注册器。

    从数据库加载已启用的外部 MCP Server 和 Tool，
    然后把外部 MCP Tool 包装成 NexusAI 内部 Tool。
    """

    def __init__(self, store: McpStore | None = None) -> None:
        self.store = store or McpStore()

    def load_servers(self) -> list[McpServerConfig]:
        return self.store.list_servers(enabled=True)

    def load_tool_specs(self, server: McpServerConfig) -> list[McpToolSpec]:
        return self.store.list_tools(
            server_name=server.name,
            enabled=True,
        )

    def register_to_tool_registry(self, tool_registry: ToolRegistry) -> None:
        for server in self.load_servers():
            if not server.enabled:
                continue

            for spec in self.load_tool_specs(server):
                if not spec.enabled:
                    continue

                tool_registry.register(
                    McpToolAdapter(
                        server=server,
                        spec=spec,
                    )
                )
