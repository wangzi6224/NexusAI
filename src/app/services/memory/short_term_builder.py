from __future__ import annotations

from typing import Any

from src.app.conversation_store import get_conversation, list_recent_messages
from src.app.services.memory.short_term_store import ShortTermMemoryStore


class ShortTermMemoryBuilder:
    """构建当前会话短期记忆包。

    输出给：
    1. ContextBuilder
    2. AgentService
    3. assistant_runs.trace
    """

    def __init__(self) -> None:
        self.state_store = ShortTermMemoryStore()

    def build(
        self,
        *,
        conversation_id: str,
        recent_limit: int = 10,
    ) -> dict[str, Any]:
        conversation = get_conversation(conversation_id)
        state = self.state_store.get_state(conversation_id)
        recent_messages = list_recent_messages(conversation_id, limit=recent_limit)

        return {
            "conversation_id": conversation_id,
            "summary": conversation.get("summary") if conversation else None,
            "state": state.model_dump(mode="json") if state else None,
            "recent_messages": recent_messages,
            "trace": {
                "has_summary": bool(conversation and conversation.get("summary")),
                "has_state": bool(state),
                "recent_message_count": len(recent_messages),
            },
        }
