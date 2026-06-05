import json
from pathlib import Path
from typing import Any

from src.app.config import (
    get_default_llm_model,
    get_settings,
    normalize_cloud_provider,
    normalize_llm_provider,
)
from src.app.paths import DATA_DIR

RUNTIME_CONFIG_FILE = DATA_DIR / "runtime_config.json"


def _default_provider() -> str:
    return normalize_llm_provider(get_settings().llm_provider)


def _default_cloud_provider() -> str:
    return normalize_cloud_provider(get_settings().cloud_provider)


def _default_config() -> dict[str, Any]:
    provider = _default_provider()
    cloud_provider = _default_cloud_provider()
    return {
        "selected_provider": provider,
        "selected_cloud_provider": cloud_provider,
        "selected_model": get_default_llm_model(provider, cloud_provider),
        "selected_models": {
            "ollama": get_default_llm_model("ollama"),
            "cloud": get_default_llm_model("cloud", cloud_provider),
        },
        "selected_cloud_models": {
            "deepseek": get_default_llm_model("cloud", "deepseek"),
            "qwen": get_default_llm_model("cloud", "qwen"),
            "glm": get_default_llm_model("cloud", "glm"),
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
    return normalize_llm_provider(str(provider))


def get_selected_cloud_provider() -> str:
    data = _read_runtime_config()
    raw_provider = str(data.get("selected_provider") or "").lower().strip()
    if raw_provider in {"deepseek", "qwen", "gml", "glm"}:
        return normalize_cloud_provider(raw_provider)

    cloud_provider = data.get("selected_cloud_provider") or _default_cloud_provider()
    return normalize_cloud_provider(str(cloud_provider))


def get_selected_model(
    provider: str | None = None,
    cloud_provider: str | None = None,
) -> str:
    data = _read_runtime_config()
    provider_name = normalize_llm_provider(provider or get_selected_provider())
    selected_models = data.get("selected_models")

    if provider_name == "cloud":
        cloud_provider_name = normalize_cloud_provider(
            cloud_provider or get_selected_cloud_provider()
        )
        selected_cloud_models = data.get("selected_cloud_models")

        if (
            isinstance(selected_cloud_models, dict)
            and selected_cloud_models.get(cloud_provider_name)
        ):
            return str(selected_cloud_models[cloud_provider_name])

        if (
            cloud_provider_name == "deepseek"
            and isinstance(selected_models, dict)
            and selected_models.get("deepseek")
        ):
            return str(selected_models["deepseek"])

        if isinstance(selected_models, dict) and selected_models.get("cloud"):
            return str(selected_models["cloud"])

        return get_default_llm_model("cloud", cloud_provider_name)

    if isinstance(selected_models, dict) and selected_models.get(provider_name):
        return str(selected_models[provider_name])

    if provider_name == get_selected_provider() and data.get("selected_model"):
        return str(data["selected_model"])

    return get_default_llm_model(provider_name)


def set_selected_model(
    model: str,
    provider: str | None = None,
    cloud_provider: str | None = None,
) -> None:
    provider_name = normalize_llm_provider(provider or get_selected_provider())
    data = {**_default_config(), **_read_runtime_config()}
    selected_models = data.get("selected_models")

    if not isinstance(selected_models, dict):
        selected_models = {}

    if provider_name == "cloud":
        cloud_provider_name = normalize_cloud_provider(
            cloud_provider or get_selected_cloud_provider()
        )
        selected_cloud_models = data.get("selected_cloud_models")
        if not isinstance(selected_cloud_models, dict):
            selected_cloud_models = {}

        selected_cloud_models[cloud_provider_name] = model
        selected_models["cloud"] = model
        data["selected_cloud_provider"] = cloud_provider_name
        data["selected_cloud_models"] = selected_cloud_models
    else:
        selected_models[provider_name] = model

    data["selected_provider"] = provider_name
    data["selected_model"] = model
    data["selected_models"] = selected_models

    _write_runtime_config(data)
