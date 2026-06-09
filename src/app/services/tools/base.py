from abc import ABC, abstractmethod
from typing import Any, Literal


class Tool(ABC):
    """Agent 可调用工具的基础抽象。"""

    name: str
    description: str
    parameters: dict[str, Any]

    source: Literal["internal", "mcp"] = "internal"
    risk_level: Literal["low", "medium", "high"] = "low"

    @abstractmethod
    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
