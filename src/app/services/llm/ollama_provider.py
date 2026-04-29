import requests
import json
from collections.abc import Iterator
from src.app.exceptions import LLMProviderError

from src.app.config import (
    get_settings,
)
from src.app.services.llm.base import LLMProvider, LLMResponse, LLMUsage, LLMStreamChunk, OllamaConfig


class OllamaProvider(LLMProvider):
    name = "ollama"

    # 从配置中获取 Ollama 相关设置
    def _get_ollama_config(self) -> OllamaConfig:
        return {
            "base_url": get_settings().ollama_base_url,
            "model": get_settings().ollama_model,
            "timeout": get_settings().ollama_timeout,
            "keep_alive": get_settings().ollama_keep_alive,
        }

    def chat(self, messages: list[dict[str, str]], model: str | None = None) -> LLMResponse:
        # 获取配置信息
        config = self._get_ollama_config()
        base_url = config["base_url"]
        selected_model = model or config["model"]
        timeout = config["timeout"]
        keep_alive = config["keep_alive"]

        # 构建请求
        url = f"{base_url}/api/chat"

        # 构建请求负载
        payload = {
                "model": selected_model,
                "messages": messages,
                "stream": False,
                "keep_alive": keep_alive,
            }

        try:
            response = requests.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as exc:
            raise LLMProviderError("请求 Ollama 超时，请检查模型是否正在加载，或机器性能是否不足") from exc
        except requests.exceptions.HTTPError as exc:
            error_response = exc.response
            status_code = error_response.status_code if error_response is not None else "unknown"
            response_text = error_response.text if error_response is not None else str(exc)
            raise LLMProviderError(
                f"Ollama HTTP 请求失败，状态码: {status_code}，响应内容: {response_text}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise LLMProviderError(f"请求 Ollama 失败: {exc}") from exc

        data = response.json()

        try:
            content = data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise RuntimeError(f"Ollama 返回结构异常: {data}") from exc

        usage = LLMUsage(
            prompt_tokens=data.get("prompt_eval_count", 0) or 0,
            completion_tokens=data.get("eval_count", 0) or 0,
            total_tokens=(data.get("prompt_eval_count", 0) or 0) + (data.get("eval_count", 0) or 0),
        )

        return LLMResponse(
            content=content,
            provider=self.name,
            model=selected_model,
            usage=usage,
        )

    def stream_chat(self, messages: list[dict[str, str]], model: str | None = None) -> Iterator[LLMStreamChunk]:
        config = self._get_ollama_config()
        base_url = config["base_url"]
        selected_model = model or config["model"]
        timeout = config["timeout"]
        keep_alive = config["keep_alive"]

        playload = {
                "model": selected_model,
                "messages": messages,
                "stream": True,
                "keep_alive": keep_alive,
            }

        url = f"{base_url}/api/chat"

        try:
            with requests.post(url, json=playload, timeout=timeout, stream=True) as response:
                response.raise_for_status()

                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise LLMProviderError(
                            message="Ollama 流式返回不是合法 JSON",
                            detail=line,
                        ) from exc

                    if data.get("done"):
                        yield LLMStreamChunk(delta="", done=True)
                        break

                    delta = data.get("message", {}).get("content", "")

                    if delta:
                        yield LLMStreamChunk(delta=delta, done=False)
 
            
        except requests.exceptions.Timeout as exc:
            raise LLMProviderError(
                message="Ollama 流式请求超时",
                detail=str(exc),
            ) from exc
        except requests.exceptions.HTTPError as exc:
            error_response = exc.response
            status_code = error_response.status_code if error_response is not None else "unknown"
            response_text = error_response.text if error_response is not None else str(exc)

            raise LLMProviderError(
                message="Ollama 流式 HTTP 请求失败",
                detail=f"状态码: {status_code}，响应内容: {response_text}",
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise LLMProviderError(
                message="Ollama 流式请求失败",
                detail=str(exc),
            ) from exc
