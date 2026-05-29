from src.app.config import get_agent_allowed_tools
from src.app.services.tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        self.allowed_tools = set(get_agent_allowed_tools())

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"工具已注册: {tool.name}")

        if tool.name not in self.allowed_tools:
            return

        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self.allowed_tools:
            raise PermissionError(f"工具不在白名单中: {name}")

        tool = self._tools.get(name)

        if tool is None:
            raise ValueError(f"未知工具: {name}")

        return tool

    def list_tools(self) -> list[dict]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self._tools.values()
        ]
