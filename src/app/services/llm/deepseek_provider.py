from collections.abc import Iterable, Iterator
from typing import NoReturn, cast

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    OpenAIError,
)
from openai.types.chat import ChatCompletionMessageParam

from src.app.config import get_settings
from src.app.exceptions import LLMProviderError
from src.app.services.llm.base import (
    DeepSeekConfig,
    LLMProvider,
    LLMResponse,
    LLMStreamChunk,
    LLMUsage,
)


class DeepSeekProvider(LLMProvider):
    name = "deepseek"

    def _get_deepseek_config(self) -> DeepSeekConfig:
        settings = get_settings()
        return {
            "base_url": settings.deepseek_base_url.rstrip("/"),
            "api_key": settings.deepseek_api_key,
            "model": settings.deepseek_model,
            "timeout": settings.deepseek_timeout,
            "thinking_enabled": settings.deepseek_thinking_enabled,
        }

    def _client(self, config: DeepSeekConfig) -> OpenAI:
        api_key = config["api_key"]
        if not api_key:
            raise LLMProviderError(
                "DeepSeek API Key 未配置，请在 .env 中填写 DEEPSEEK_API_KEY"
            )

        return OpenAI(
            api_key=api_key,
            base_url=config["base_url"],
            timeout=config["timeout"],
        )

    def _extra_body(self, thinking_enabled: bool) -> dict[str, object]:
        return {
            "thinking": {
                "type": "enabled" if thinking_enabled else "disabled",
            },
        }

    def _messages(
        self,
        messages: list[dict[str, str]],
    ) -> Iterable[ChatCompletionMessageParam]:
        return cast(Iterable[ChatCompletionMessageParam], messages)

    def _handle_api_status_error(self, exc: APIStatusError, message: str) -> NoReturn:
        response_text = getattr(exc.response, "text", None) or str(exc)
        raise LLMProviderError(
            message=message,
            detail=f"状态码: {exc.status_code}，响应内容: {response_text}",
        ) from exc

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> LLMResponse:
        config = self._get_deepseek_config()
        selected_model = model or config["model"]
        client = self._client(config)

        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=self._messages(messages),
                extra_body=self._extra_body(config["thinking_enabled"]),
            )
        except APITimeoutError as exc:
            raise LLMProviderError(
                "请求 DeepSeek 超时，请稍后重试或调大 DEEPSEEK_TIMEOUT"
            ) from exc
        except APIStatusError as exc:
            self._handle_api_status_error(exc, "DeepSeek HTTP 请求失败")
        except APIConnectionError as exc:
            raise LLMProviderError(f"请求 DeepSeek 失败: {exc}") from exc
        except OpenAIError as exc:
            raise LLMProviderError(f"请求 DeepSeek 失败: {exc}") from exc

        try:
            content = response.choices[0].message.content or ""
        except (AttributeError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                f"DeepSeek 返回结构异常: {response.model_dump()}"
            ) from exc

        usage_data = response.usage
        usage = LLMUsage(
            prompt_tokens=usage_data.prompt_tokens if usage_data else 0,
            completion_tokens=usage_data.completion_tokens if usage_data else 0,
            total_tokens=usage_data.total_tokens if usage_data else 0,
        )

        return LLMResponse(
            content=content,
            provider=self.name,
            model=response.model or selected_model,
            usage=usage,
        )

    def structured_chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> LLMResponse:
        config = self._get_deepseek_config()
        selected_model = model or config["model"]
        client = self._client(config)

        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=self._messages(messages),
                extra_body=self._extra_body(config["thinking_enabled"]),
                response_format={"type": "json_object"},
            )
        except APITimeoutError as exc:
            raise LLMProviderError(
                "请求 DeepSeek 超时，请稍后重试或调大 DEEPSEEK_TIMEOUT"
            ) from exc
        except APIStatusError as exc:
            self._handle_api_status_error(exc, "DeepSeek HTTP 请求失败")
        except APIConnectionError as exc:
            raise LLMProviderError(f"请求 DeepSeek 失败: {exc}") from exc
        except OpenAIError as exc:
            raise LLMProviderError(f"请求 DeepSeek 失败: {exc}") from exc

        try:
            content = response.choices[0].message.content or ""
        except (AttributeError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                f"DeepSeek 返回结构异常或非 JSON 对象: {response.model_dump()}"
            ) from exc

        usage_data = response.usage
        usage = LLMUsage(
            prompt_tokens=usage_data.prompt_tokens if usage_data else 0,
            completion_tokens=usage_data.completion_tokens if usage_data else 0,
            total_tokens=usage_data.total_tokens if usage_data else 0,
        )

        return LLMResponse(
            content=content,
            provider=self.name,
            model=response.model or selected_model,
            usage=usage,
        )

    def stream_chat(
        self,
        message: list[dict[str, str]],
        model: str | None = None,
    ) -> Iterator[LLMStreamChunk]:
        config = self._get_deepseek_config()
        selected_model = model or config["model"]
        client = self._client(config)

        try:
            stream = client.chat.completions.create(
                model=selected_model,
                messages=self._messages(message),
                stream=True,
                extra_body=self._extra_body(config["thinking_enabled"]),
            )

            for chunk in stream:
                choices = chunk.choices or []
                if not choices:
                    continue

                choice = choices[0]
                delta = choice.delta.content or ""
                chunk_model = chunk.model or selected_model

                if delta:
                    yield LLMStreamChunk(
                        delta=delta,
                        done=False,
                        model=chunk_model,
                    )

                if choice.finish_reason:
                    yield LLMStreamChunk(
                        delta="",
                        done=True,
                        model=chunk_model,
                    )
                    break
        except APITimeoutError as exc:
            raise LLMProviderError(
                message="DeepSeek 流式请求超时",
                detail=str(exc),
            ) from exc
        except APIStatusError as exc:
            self._handle_api_status_error(exc, "DeepSeek 流式 HTTP 请求失败")
        except APIConnectionError as exc:
            raise LLMProviderError(
                message="DeepSeek 流式请求失败",
                detail=str(exc),
            ) from exc
        except OpenAIError as exc:
            raise LLMProviderError(
                message="DeepSeek 流式请求失败",
                detail=str(exc),
            ) from exc
