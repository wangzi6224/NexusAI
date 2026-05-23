from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """
    Agent 可调用工具的基础抽象。

    注意：
    1. Tool 不是 FastAPI 路由
    2. Tool 是 Agent 内部能力
    3. Tool 必须返回结构化 dict
    """

    name: str
    description: str
    parameters: dict[str, Any]

    @abstractmethod
    def run(self, arguments: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
