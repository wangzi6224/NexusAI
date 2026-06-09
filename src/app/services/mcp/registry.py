from __future__ import annotations

from src.app.services.mcp.schemas import McpServerConfig, McpToolSpec
from src.app.services.mcp.tool_adapter import McpToolAdapter
from src.app.services.tools.registry import ToolRegistry


class McpRegistry:
    """MCP 工具注册器。

    第一版使用静态配置。
    后续可以从数据库 mcp_server_configs 读取。
    """

    def load_servers(self) -> list[McpServerConfig]:
        return [
            # 示例：后续根据实际外部 MCP Server 修改
            # McpServerConfig(
            #     name="github",
            #     command="npx",
            #     args=["-y", "@modelcontextprotocol/server-github"],
            #     env={"GITHUB_PERSONAL_ACCESS_TOKEN": "..."},
            # ),
        ]

    def load_tool_specs(self, server: McpServerConfig) -> list[McpToolSpec]:
        # 第一版不要自动信任外部工具列表。
        # 明确声明允许接入哪些工具。
        return []

    def register_to_tool_registry(self, tool_registry: ToolRegistry) -> None:
        for server in self.load_servers():
            if not server.enabled:
                continue

            for spec in self.load_tool_specs(server):
                tool_registry.register(
                    McpToolAdapter(
                        server=server,
                        spec=spec,
                    )
                )
