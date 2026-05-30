import json
from collections.abc import Iterator

import requests

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

    def _headers(self, api_key: str) -> dict[str, str]:
        if not api_key:
            raise LLMProviderError(
                "DeepSeek API Key 未配置，请在 .env 中填写 DEEPSEEK_API_KEY"
            )

        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _payload(
        self,
        messages: list[dict[str, str]],
        model: str,
        stream: bool,
        thinking_enabled: bool,
    ) -> dict[str, object]:
        return {
            "model": model,
            "messages": messages,
            "stream": stream,
            "thinking": {
                "type": "enabled" if thinking_enabled else "disabled",
            },
        }

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> LLMResponse:
        config = self._get_deepseek_config()
        selected_model = model or config["model"]
        url = f"{config['base_url']}/chat/completions"
        payload = self._payload(
            messages=messages,
            model=selected_model,
            stream=False,
            thinking_enabled=config["thinking_enabled"],
        )

        try:
            response = requests.post(
                url,
                headers=self._headers(config["api_key"]),
                json=payload,
                timeout=config["timeout"],
            )
            response.raise_for_status()
        except requests.exceptions.Timeout as exc:
            raise LLMProviderError("请求 DeepSeek 超时，请稍后重试或调大 DEEPSEEK_TIMEOUT") from exc
        except requests.exceptions.HTTPError as exc:
            error_response = exc.response
            status_code = (
                error_response.status_code if error_response is not None else "unknown"
            )
            response_text = error_response.text if error_response is not None else str(exc)
            raise LLMProviderError(
                f"DeepSeek HTTP 请求失败，状态码: {status_code}，响应内容: {response_text}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise LLMProviderError(f"请求 DeepSeek 失败: {exc}") from exc

        data = response.json()

        try:
            choice = data["choices"][0]
            content = choice["message"].get("content") or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(f"DeepSeek 返回结构异常: {data}") from exc

        usage_data = data.get("usage") or {}
        usage = LLMUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0) or 0,
            completion_tokens=usage_data.get("completion_tokens", 0) or 0,
            total_tokens=usage_data.get("total_tokens", 0) or 0,
        )

        return LLMResponse(
            content=content,
            provider=self.name,
            model=data.get("model") or selected_model,
            usage=usage,
        )

    def stream_chat(
        self,
        message: list[dict[str, str]],
        model: str | None = None,
    ) -> Iterator[LLMStreamChunk]:
        config = self._get_deepseek_config()
        selected_model = model or config["model"]
        url = f"{config['base_url']}/chat/completions"
        payload = self._payload(
            messages=message,
            model=selected_model,
            stream=True,
            thinking_enabled=config["thinking_enabled"],
        )

        try:
            with requests.post(
                url,
                headers=self._headers(config["api_key"]),
                json=payload,
                timeout=config["timeout"],
                stream=True,
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if not line.startswith("data:"):
                        continue

                    raw_data = line.removeprefix("data:").strip()
                    if raw_data == "[DONE]":
                        yield LLMStreamChunk(
                            delta="",
                            done=True,
                            model=selected_model,
                        )
                        break

                    try:
                        data = json.loads(raw_data)
                    except json.JSONDecodeError as exc:
                        raise LLMProviderError(
                            message="DeepSeek 流式返回不是合法 JSON",
                            detail=raw_data,
                        ) from exc

                    choices = data.get("choices") or []
                    if not choices:
                        continue

                    choice = choices[0]
                    delta_data = choice.get("delta") or {}
                    delta = delta_data.get("content") or ""

                    if delta:
                        yield LLMStreamChunk(
                            delta=delta,
                            done=False,
                            model=data.get("model") or selected_model,
                        )

                    if choice.get("finish_reason"):
                        yield LLMStreamChunk(
                            delta="",
                            done=True,
                            model=data.get("model") or selected_model,
                        )
                        break
        except requests.exceptions.Timeout as exc:
            raise LLMProviderError(
                message="DeepSeek 流式请求超时",
                detail=str(exc),
            ) from exc
        except requests.exceptions.HTTPError as exc:
            error_response = exc.response
            status_code = (
                error_response.status_code if error_response is not None else "unknown"
            )
            response_text = error_response.text if error_response is not None else str(exc)
            raise LLMProviderError(
                message="DeepSeek 流式 HTTP 请求失败",
                detail=f"状态码: {status_code}，响应内容: {response_text}",
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise LLMProviderError(
                message="DeepSeek 流式请求失败",
                detail=str(exc),
            ) from exc
