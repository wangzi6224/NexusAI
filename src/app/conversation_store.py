import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from src.app.config import get_ollama_model
from src.app.exceptions import ConversationError
from src.app.paths import DATA_DIR

CONVERSATIONS_FILE = DATA_DIR / "conversations.json"
MESSAGES_FILE = DATA_DIR / "messages.json"

ALLOWED_MESSAGE_ROLES: set[str] = {"system", "user", "assistant", "tool"}


# TODO: 后续可以改成 SQLite 或其他轻量级数据库，目前先用 JSON 文件存储，方便查看和调试
def _now_iso() -> str:
    return datetime.now().isoformat()


# 辅助函数：确保 JSON 文件存在，并且是一个数组格式
def _ensure_json_file(path: Path) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text("[]", encoding="utf-8")


# 辅助函数：加载 JSON 文件并返回数组数据，如果文件内容不合法则抛出异常
def _load_json_list(path: Path) -> list[dict[str, Any]]:
    _ensure_json_file(path)

    try:
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        data = json.loads(content)

        if not isinstance(data, list):
            raise ConversationError(
                message="JSON 存储格式错误",
                detail=f"{path} 内容不是数组",
                status_code=500,
            )

        return data

    except json.JSONDecodeError as exc:
        raise ConversationError(
            message="读取 JSON 失败",
            detail=f"{path}: {exc}",
            status_code=500,
        ) from exc


def _save_json_list(path: Path, items: list[dict[str, Any]]) -> None:
    _ensure_json_file(path)

    try:
        path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        raise ConversationError(
            message="写入 JSON 失败",
            detail=f"{path}: {exc}",
            status_code=500,
        ) from exc


def load_conversations() -> list[dict[str, Any]]:
    return _load_json_list(CONVERSATIONS_FILE)


def save_conversations(conversations: list[dict[str, Any]]) -> None:
    _save_json_list(CONVERSATIONS_FILE, conversations)


def create_conversation(title: str, model: str | None = None) -> dict[str, Any]:
    now = _now_iso()

    conversation = {
        "id": str(uuid.uuid4()),
        "title": title,
        "summary": None,
        "summarized_message_count": 0,
        "summary_updated_at": None,
        "model": model or get_ollama_model(),
        "provider": "ollama",
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }

    conversations = load_conversations()
    conversations.append(conversation)
    save_conversations(conversations)

    return conversation


def list_conversations() -> list[dict[str, Any]]:
    conversations = load_conversations()
    return sorted(
        conversations,
        key=lambda item: item.get("updated_at", ""),
        reverse=True,
    )


def get_conversation(conversation_id: str) -> dict[str, Any] | None:
    conversations = load_conversations()

    for conversation in conversations:
        if conversation["id"] == conversation_id:
            return conversation

    return None


def update_conversation(
    conversation_id: str,
    updates: dict[str, Any],
) -> dict[str, Any]:
    conversations = load_conversations()

    for conversation in conversations:
        if conversation["id"] == conversation_id:
            conversation.update(updates)
            conversation["updated_at"] = _now_iso()
            save_conversations(conversations)
            return conversation

    raise ConversationError(
        message="会话不存在",
        detail=f"conversation_id={conversation_id}",
        status_code=404,
    )


def load_messages() -> list[dict[str, Any]]:
    return _load_json_list(MESSAGES_FILE)


def save_messages(messages: list[dict[str, Any]]) -> None:
    _save_json_list(MESSAGES_FILE, messages)


def create_message(
    conversation_id: str,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if role not in ALLOWED_MESSAGE_ROLES:
        raise ConversationError(
            message="非法消息角色",
            detail=f"role={role}",
            status_code=400,
        )

    message = {
        "id": str(uuid.uuid4()),
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "metadata": metadata or {},
        "created_at": _now_iso(),
    }

    messages = load_messages()
    messages.append(message)
    save_messages(messages)

    return message


def list_messages(conversation_id: str) -> list[dict[str, Any]]:
    messages = load_messages()
    return [
        message for message in messages if message["conversation_id"] == conversation_id
    ]


def list_recent_messages(
    conversation_id: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    messages = list_messages(conversation_id)
    return messages[-limit:]


def count_messages(conversation_id: str) -> int:
    return len(list_messages(conversation_id))
