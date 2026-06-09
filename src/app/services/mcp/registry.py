from __future__ import annotations

from src.app.services.mcp.schemas import McpServerConfig, McpToolSpec
from src.app.services.mcp.tool_adapter import McpToolAdapter
from src.app.services.tools.registry import ToolRegistry


class McpRegistry:
    """外部 MCP 工具注册器。

    这个模块负责把“第三方 MCP Server 暴露的工具”
    注册进 NexusAI 自己的 ToolRegistry。

    注意：
    这里不是 NexusAI 对外提供 MCP Server。
    对外 MCP Server 在 mcp-server/ 目录下。

    这里是 NexusAI 作为 MCP Client，
    主动连接外部 MCP Server，例如 GitHub、文件系统、搜索服务等，
    然后把外部工具包装成内部 Tool，交给 Agent 调用。

    当前第一版是静态配置：
    1. load_servers() 声明允许连接哪些外部 MCP Server
    2. load_tool_specs() 声明允许使用这些 Server 的哪些工具
    3. register_to_tool_registry() 把这些工具注册进 Agent ToolRegistry

    为什么不自动信任 tools/list？
    因为外部 MCP Server 可能暴露高风险工具，例如写文件、执行命令、删除数据。
    所以第一版必须显式 allowlist，只接入明确声明过的低风险工具。
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
        """把 MCP 工具注册到 NexusAI 的 ToolRegistry 中。"""
        for server in self.load_servers():
            if not server.enabled:
                continue

            for spec in self.load_tool_specs(server):
                mcp_tools = McpToolAdapter(
                    server=server,
                    spec=spec,
                )
                tool_registry.register(mcp_tools)
