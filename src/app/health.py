import requests

from src.app.config import get_ollama_base_url, get_ollama_model, get_ollama_timeout


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
    
def get_available_models() -> list[str]:
    base_url = get_ollama_base_url()
    timeout = get_ollama_timeout()

    response = requests.get(f"{base_url}/api/tags", timeout=timeout)
    response.raise_for_status()
    data = response.json()

    models = data.get("models", [])
    return [item.get("name", "") for item in models if item.get("name")]
