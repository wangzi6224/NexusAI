import json
from pathlib import Path
from typing import Any

from src.app.config import get_default_llm_model, get_settings
from src.app.paths import DATA_DIR

RUNTIME_CONFIG_FILE = DATA_DIR / "runtime_config.json"


def _default_provider() -> str:
    return get_settings().llm_provider.lower().strip()


def _default_config() -> dict[str, Any]:
    provider = _default_provider()
    return {
        "selected_provider": provider,
        "selected_model": get_default_llm_model(provider),
        "selected_models": {
            "ollama": get_default_llm_model("ollama"),
            "deepseek": get_default_llm_model("deepseek"),
        },
    }


def _ensure_runtime_config_file() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not RUNTIME_CONFIG_FILE.exists():
        RUNTIME_CONFIG_FILE.write_text(
            json.dumps(_default_config(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return RUNTIME_CONFIG_FILE


def _read_runtime_config() -> dict[str, Any]:
    path = _ensure_runtime_config_file()
    content = path.read_text(encoding="utf-8").strip()

    if not content:
        return _default_config()

    try:
        data = json.loads(content)
        if isinstance(data, dict):
            return data
        return _default_config()
    except json.JSONDecodeError:
        return _default_config()


def _write_runtime_config(data: dict[str, Any]) -> None:
    path = _ensure_runtime_config_file()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_selected_provider() -> str:
    data = _read_runtime_config()
    provider = data.get("selected_provider") or _default_provider()
    return str(provider).lower().strip()


def get_selected_model(provider: str | None = None) -> str:
    data = _read_runtime_config()
    provider_name = (provider or get_selected_provider()).lower().strip()
    selected_models = data.get("selected_models")

    if isinstance(selected_models, dict) and selected_models.get(provider_name):
        return str(selected_models[provider_name])

    if provider_name == get_selected_provider() and data.get("selected_model"):
        return str(data["selected_model"])

    return get_default_llm_model(provider_name)


def set_selected_model(model: str, provider: str | None = None) -> None:
    provider_name = (provider or get_selected_provider()).lower().strip()
    data = {**_default_config(), **_read_runtime_config()}
    selected_models = data.get("selected_models")

    if not isinstance(selected_models, dict):
        selected_models = {}

    selected_models[provider_name] = model
    data["selected_provider"] = provider_name
    data["selected_model"] = model
    data["selected_models"] = selected_models

    _write_runtime_config(data)
