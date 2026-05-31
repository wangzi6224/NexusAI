import requests
from src.app.exceptions import LLMProviderError

from src.app.config import (
    get_ollama_base_url,
    get_ollama_model,
    get_ollama_timeout,
    get_settings,
)


def check_ollama_server() -> tuple[bool, str]:
    base_url = get_ollama_base_url()
    timeout = get_ollama_timeout()

    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        response.raise_for_status()
        return True, "Ollama 服务连接正常"
    except requests.RequestException as exc:
        return False, f"Ollama 服务不可用: {exc}"


def check_ollama_model_exists() -> tuple[bool, str]:
    base_url = get_ollama_base_url()
    timeout = get_ollama_timeout()
    model = get_ollama_model()

    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        response.raise_for_status()
        data = response.json()

        models = data.get("models", [])
        names = [item.get("name", "") for item in models]

        if model in names:
            return True, f"模型存在: {model}"

        return False, f"模型不存在: {model}，当前可用模型: {names}"
    except requests.RequestException as exc:
        return False, f"检查模型失败: {exc}"


def get_available_models(provider: str | None = None) -> list[str]:
    provider_name = (provider or "ollama").lower().strip()

    if provider_name == "deepseek":
        return [get_settings().deepseek_model]

    if provider_name != "ollama":
        raise LLMProviderError(
            message="不支持的 Provider",
            detail=f"provider={provider_name}",
        )

    base_url = get_ollama_base_url()
    timeout = get_ollama_timeout()

    try:
        response = requests.get(f"{base_url}/api/tags", timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise LLMProviderError(
            message="获取模型列表超时",
            detail=str(exc),
        ) from exc
    except requests.exceptions.HTTPError as exc:
        error_response = exc.response
        status_code = (
            error_response.status_code if error_response is not None else "unknown"
        )
        response_text = error_response.text if error_response is not None else str(exc)

        raise LLMProviderError(
            message="获取模型列表失败",
            detail=f"状态码: {status_code}，响应内容: {response_text}",
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise LLMProviderError(
            message="Ollama 服务不可用，无法获取模型列表",
            detail=str(exc),
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise LLMProviderError(
            message="Ollama 模型列表返回格式异常",
            detail=response.text,
        ) from exc

    models = data.get("models", [])
    return [item.get("name", "") for item in models if item.get("name")]
