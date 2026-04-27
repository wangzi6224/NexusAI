import requests

from src.app.config import (
    get_ollama_base_url,
    get_ollama_keep_alive,
    get_ollama_timeout,
)
from src.app.runtime_config import get_selected_model
from src.app.services.llm.base import LLMProvider, LLMResponse, LLMUsage


class OllamaProvider(LLMProvider):
    name = "ollama"

    def chat(self, messages: list[dict[str, str]], model: str | None = None) -> LLMResponse:
        # 获取配置信息
        base_url = get_ollama_base_url()
        selected_model = model or get_selected_model()
        timeout = get_ollama_timeout()
        keep_alive = get_ollama_keep_alive()

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
            raise RuntimeError("请求 Ollama 超时，请检查模型是否正在加载，或机器性能是否不足") from exc
        except requests.exceptions.HTTPError as exc:
            error_response = exc.response
            status_code = error_response.status_code if error_response is not None else "unknown"
            response_text = error_response.text if error_response is not None else str(exc)
            raise RuntimeError(
                f"Ollama HTTP 请求失败，状态码: {status_code}，响应内容: {response_text}"
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(f"请求 Ollama 失败: {exc}") from exc

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
