import os
from dotenv import load_dotenv

load_dotenv()


def get_ollama_base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def get_ollama_model() -> str:
    model = os.getenv("OLLAMA_MODEL")
    if not model:
        raise ValueError("缺少 OLLAMA_MODEL，请检查 .env 文件")
    return model


def get_ollama_timeout() -> int:
    value = os.getenv("OLLAMA_TIMEOUT", "120")
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError("OLLAMA_TIMEOUT 必须是整数") from exc


def get_ollama_keep_alive() -> str:
    return os.getenv("OLLAMA_KEEP_ALIVE", "5m")


def get_log_level() -> str:
    return os.getenv("APP_LOG_LEVEL", "INFO")


def get_chat_history_path() -> str:
    return os.getenv("CHAT_HISTORY_PATH", "chat_history.json")
