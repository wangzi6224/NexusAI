from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from typing import TypedDict


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class OllamaConfig(TypedDict):
    base_url: str
    model: str
    timeout: int
    keep_alive: str


@dataclass
class DeepSeekConfig(TypedDict):
    base_url: str
    api_key: str
    model: str
    timeout: int
    thinking_enabled: bool


@dataclass
class CloudConfig(TypedDict):
    cloud_provider: str
    display_name: str
    base_url: str
    api_key: str
    api_key_env: str
    model: str
    timeout: int
    thinking_enabled: bool


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    usage: LLMUsage


@dataclass
class LLMStreamChunk:
    delta: str
    done: bool = False
    model: str | None = None
    latency_ms: int | None = None


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def chat(
        self, messages: list[dict[str, str]], model: str | None = None
    ) -> LLMResponse:
        """调用聊天模型并返回统一结构。"""
        raise NotImplementedError

    def structured_chat(
        self, messages: list[dict[str, str]], model: str | None = None
    ) -> LLMResponse:
        """调用聊天模型并返回结构化响应。"""
        raise NotImplementedError

    @abstractmethod
    def stream_chat(
        self, message: list[dict[str, str]], model: str | None = None
    ) -> Iterator[LLMStreamChunk]:
        """调用聊天模型并以流式方式返回响应。"""
        raise NotImplementedError
