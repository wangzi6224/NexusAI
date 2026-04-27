from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    usage: LLMUsage


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], model: str | None = None) -> LLMResponse:
        """调用聊天模型并返回统一结构。"""
        raise NotImplementedError
