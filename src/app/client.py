import requests

from src.app.config import (
    get_ollama_base_url,
    get_ollama_keep_alive,
    get_ollama_timeout,
)
from src.app.runtime_config import get_selected_model


def chat_completion(user_input: str) -> str:
    base_url = get_ollama_base_url()
    model = get_selected_model()
    timeout = get_ollama_timeout()
    keep_alive = get_ollama_keep_alive()

    url = f"{base_url}/api/chat"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": user_input,
            }
        ],
        "stream": False,
        "keep_alive": keep_alive,
    }

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise RuntimeError("请求 Ollama 超时，请检查模型加载状态或机器性能") from exc
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"Ollama HTTP 请求失败，状态码: {response.status_code}，响应内容: {response.text}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"请求 Ollama 失败: {exc}") from exc

    data = response.json()

    try:
        return data["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError(f"Ollama 返回结构异常: {data}") from exc
