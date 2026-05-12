from typing import Any

from src.app.conversation_store import get_conversation, list_recent_messages
from src.app.exceptions import ConversationError
from src.app.schemas import ContextPreviewResponse

DEFAULT_SYSTEM_PROMPT = (
    "你是一个专业、耐心、严谨的 AI 开发学习助手。请使用简体中文回答。"
)

MAX_RECENT_MESSAGES = 10
MAX_CONTEXT_CHARS = 12000

ALLOWED_CONTEXT_ROLES = {"system", "user", "assistant", "tool"}


class ContextBuilder:
    def __init__(
        self,
        max_recent_messages: int = MAX_RECENT_MESSAGES,
        max_context_chars: int = MAX_CONTEXT_CHARS,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        self.max_recent_messages = max_recent_messages
        self.max_context_chars = max_context_chars
        self.system_prompt = system_prompt

    # 确保会话存在，如果不存在则抛出异常
    def _ensure_conversation_exists(self, conversation_id: str) -> dict[str, Any]:
        conversation = get_conversation(conversation_id)

        if conversation is None:
            raise ConversationError(
                message="会话不存在",
                detail=f"conversation_id={conversation_id}",
                status_code=404,
            )

        return conversation

    # 估算token大小
    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0

        chinese_chars = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        other_chars = len(text) - chinese_chars

        return chinese_chars + max(1, other_chars // 4)

    def estimate_messages_tokens(self, messages: list[dict[str, str]]) -> int:
        return sum(self.estimate_tokens(message["content"]) for message in messages)

    def _messages_chars(self, messages: list[dict[str, str]]) -> int:
        return sum(len(message["content"]) for message in messages)

    def build_messages(self, conversation_id: str) -> list[dict[str, str]]:
        """
        核心流程：
        1. 先放 system prompt
        2. 如果有 summary，再放 summary system message
        3. 读取最近 N 条 messages
        4. 从最新消息往前尝试加入
        5. 超过字符限制就停止
        6. reverse 回正常时间顺序
        """
        conversation: dict[str, Any] = self._ensure_conversation_exists(conversation_id)

        base_messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": self.system_prompt,
            }
        ]

        summary = conversation.get("summary")
        if summary:
            base_messages.append(
                {
                    "role": "system",
                    "content": f"当前会话摘要：{summary}",
                }
            )

        recent_messages = list_recent_messages(
            conversation_id,
            limit=self.max_recent_messages,
        )

        selected_recent_messages: list[dict[str, str]] = []
        current_chars = self._messages_chars(base_messages)

        for message in reversed(recent_messages):
            role = message.get("role")
            content = message.get("content", "")

            if role not in ALLOWED_CONTEXT_ROLES:
                continue

            normalized_message = {
                "role": role,
                "content": content,
            }

            next_chars = current_chars + len(content)

            if next_chars > self.max_context_chars:
                break

            selected_recent_messages.append(normalized_message)
            current_chars = next_chars

        selected_recent_messages.reverse()

        return base_messages + selected_recent_messages

    def build_preview(self, conversation_id: str) -> dict[str, Any]:
        conversation = self._ensure_conversation_exists(conversation_id)
        messages = self.build_messages(conversation_id)

        recent_message_count = sum(
            1
            for message in messages
            if message["role"] in {"user", "assistant", "tool"}
        )

        return {
            "conversation_id": conversation_id,
            "summary": conversation.get("summary"),
            "recent_message_count": recent_message_count,
            "estimated_tokens": self.estimate_messages_tokens(messages),
            "estimated_chars": self._messages_chars(messages),
            "max_recent_messages": self.max_recent_messages,
            "max_context_chars": self.max_context_chars,
            "messages": messages,
        }
