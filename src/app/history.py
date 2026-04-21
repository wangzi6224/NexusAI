import json
from pathlib import Path
from typing import Any

from src.app.config import get_chat_history_path


def _ensure_history_file() -> Path:
    path = Path(get_chat_history_path())

    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text("[]", encoding="utf-8")

    return path


def load_history() -> list[dict[str, Any]]:
    path = _ensure_history_file()
    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []
        return json.loads(content)
    except json.JSONDecodeError:
        return []


def append_history(record: dict[str, Any]) -> None:
    path = _ensure_history_file()
    history = load_history()
    history.append(record)
    path.write_text(
        json.dumps(history, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
