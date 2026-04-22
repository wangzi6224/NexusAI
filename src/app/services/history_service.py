from typing import Any

from src.app.history import clear_history, load_history

def get_history() -> list[dict[str, Any]]:
    return load_history()

def clear_chat_history() -> None:
    clear_history()
