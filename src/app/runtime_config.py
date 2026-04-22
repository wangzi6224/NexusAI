import json
from pathlib import Path

from src.app.config import get_ollama_model
from src.app.paths import DATA_DIR

RUNTIME_CONFIG_FILE = DATA_DIR / "runtime_config.json"


def _ensure_runtime_config_file() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not RUNTIME_CONFIG_FILE.exists():
        RUNTIME_CONFIG_FILE.write_text(
            json.dumps({"selected_model": get_ollama_model()}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return RUNTIME_CONFIG_FILE


def get_selected_model() -> str:
    path = _ensure_runtime_config_file()
    content = path.read_text(encoding="utf-8").strip()

    if not content:
        return get_ollama_model()

    try:
        data = json.loads(content)
        return data.get("selected_model", get_ollama_model())
    except json.JSONDecodeError:
        return get_ollama_model()


def set_selected_model(model: str) -> None:
    path = _ensure_runtime_config_file()
    path.write_text(
        json.dumps({"selected_model": model}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
