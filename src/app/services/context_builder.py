from typing import Any

from src.app.conversation_store import get_conversation, list_recent_messages
from src.app.exceptions import ConversationError
from src.app.services.memory.short_term_schemas import ConversationState
from src.app.services.memory.short_term_store import ShortTermMemoryStore
from src.app.services.memory.long_term_schemas import RetrievedLongTermMemory

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
        self.state_store = ShortTermMemoryStore()

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

    def _format_conversation_state(
        self,
        conversation_id: str,
        conversation_state: dict[str, Any] | ConversationState | None = None,
    ) -> str | None:
        """
        把当前会话的结构化短期状态格式化成文本，方便放到 system prompt 里。

        返回一个可直接追加为 system 消息的文本内容，包含：
            当前会话结构化状态：
            - 当前目标：xxx
            - 当前主题：xxx
            - 已确认事实：
                - xxx
                - xxx
            - 已确认约束：
                - xxx
                - xxx
            - 当前会话偏好：
                - xxx
                - xxx
            - 待解决问题：
                - xxx
                - xxx

        如果当前会话没有短期状态，则返回 None。
        build_messages() 会将这个文本作为 system 消息追加到上下文中，
        让模型在理解用户问题时同时感知当前会话的状态信息。
        """
        if isinstance(conversation_state, ConversationState):
            state = conversation_state
        elif isinstance(conversation_state, dict):
            state = ConversationState(**conversation_state)
        else:
            state = self.state_store.get_state(conversation_id)

        if state is None:
            return None

        lines = [
            "当前会话结构化状态：",
            f"- 当前目标：{state.current_goal or '未知'}",
            f"- 当前主题：{state.current_topic or '未知'}",
        ]

        if state.confirmed_facts:
            lines.append("- 已确认事实：")
            for item in state.confirmed_facts[:8]:
                lines.append(f"  - {item}")

        if state.confirmed_constraints:
            lines.append("- 已确认约束：")
            for item in state.confirmed_constraints[:8]:
                lines.append(f"  - {item}")

        if state.user_preferences:
            lines.append("- 当前会话偏好：")
            for item in state.user_preferences[:6]:
                lines.append(f"  - {item}")

        if state.open_questions:
            lines.append("- 待解决问题：")
            for item in state.open_questions[:5]:
                lines.append(f"  - {item}")

        return "\n".join(lines)

    def _format_long_term_memory(
        self,
        long_term_memory_items: list[RetrievedLongTermMemory] | None,
    ) -> str | None:
        if not long_term_memory_items:
            return None

        lines = ["长期记忆检索结果："]

        for memory in long_term_memory_items[:8]:
            item = memory.item
            lines.append(
                (
                    f"- [{memory.rank}] 类型：{item.memory_type}；"
                    f"相关度：{memory.score:.3f}；"
                    f"重要性：{item.importance:.2f}；"
                    f"内容：{item.content}"
                )
            )

        return "\n".join(lines)

    def build_messages(
        self,
        conversation_id: str,
        conversation_state: dict[str, Any] | ConversationState | None = None,
        include_conversation_state: bool = True,
        long_term_memory_items: list[RetrievedLongTermMemory] | None = None,
    ) -> list[dict[str, str]]:
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

        conversation_state_text = None
        if include_conversation_state:
            conversation_state_text = self._format_conversation_state(
                conversation_id,
                conversation_state=conversation_state,
            )
        if conversation_state_text:
            base_messages.append(
                {
                    "role": "system",
                    "content": conversation_state_text,
                }
            )

        long_term_memory_text = self._format_long_term_memory(long_term_memory_items)
        if long_term_memory_text:
            base_messages.append(
                {
                    "role": "system",
                    "content": long_term_memory_text,
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
                # 如果当前还没有选任何最近消息，说明这条大概率是当前用户消息
                # 必须保留，否则模型看不到用户问题
                if not selected_recent_messages:
                    selected_recent_messages.append(normalized_message)
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
