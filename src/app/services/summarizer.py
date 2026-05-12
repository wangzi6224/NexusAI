# src/app/services/summarizer.py

from datetime import datetime
from typing import Any

from src.app.conversation_store import (
    count_messages,
    get_conversation,
    list_messages,
    update_conversation,
)
from src.app.exceptions import ConversationError
from src.app.services.llm.ollama_provider import OllamaProvider

SUMMARY_TRIGGER_MESSAGE_COUNT = 20
SUMMARY_KEEP_RECENT_MESSAGES = 10


class Summarizer:
    def _ensure_conversation_exists(self, conversation_id: str) -> dict[str, Any]:
        conversation: dict[str, Any] | None = get_conversation(conversation_id)

        if conversation is None:
            raise ConversationError(
                message="会话不存在",
                detail=f"conversation_id={conversation_id}",
                status_code=404,
            )

        return conversation

    def should_update(self, conversation_id: str) -> bool:
        conversation: dict[str, Any] = self._ensure_conversation_exists(conversation_id)
        total_message_count: int = count_messages(conversation_id)

        if total_message_count < SUMMARY_TRIGGER_MESSAGE_COUNT:
            return False

        summarized_message_count: int = int(
            conversation.get("summarized_message_count") or 0
        )

        if not conversation.get("summary"):
            return True

        return (
            total_message_count - summarized_message_count
            >= SUMMARY_KEEP_RECENT_MESSAGES
        )

    def _format_messages_for_summary(
        self,
        messages: list[dict[str, Any]],
    ) -> str:
        lines: list[str] = []

        for message in messages:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def build_prompt(
        self,
        messages: list[dict[str, Any]],
        previous_summary: str | None = None,
    ) -> list[dict[str, str]]:
        messages_text = self._format_messages_for_summary(messages)

        previous_summary_text = ""
        if previous_summary:
            previous_summary_text = f"已有会话摘要：\n{previous_summary}\n\n"

        user_prompt = f"""请把以下对话压缩成一段会话摘要，用于后续 AI 继续理解上下文。

要求：
1. 保留用户的核心目标。
2. 保留用户正在学习或开发的主题。
3. 保留已经确认的技术方案。
4. 保留关键文件名、函数名、接口路径、错误信息。
5. 删除寒暄、重复确认、无关内容。
6. 不要加入原文中没有的信息。
7. 使用简体中文。
8. 输出一段自然语言摘要，不要输出 JSON。

{previous_summary_text}对话内容：
{messages_text}
"""

        return [
            {
                "role": "system",
                "content": "你是一个严谨的会话摘要生成器，只能根据原始对话生成摘要。",
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

    def summarize(
        self,
        conversation_id: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        """生成会话摘要

        Args:
            conversation_id (str): 会话 ID
            model (str | None, optional): 使用的模型名称. Defaults to None.

        Raises:
            ConversationError: 会话不存在或没有可摘要的消息

        Returns:
            dict[str, Any]: 包含会话摘要和相关信息的字典
        """
        conversation = self._ensure_conversation_exists(conversation_id)
        messages = list_messages(conversation_id)

        if not messages:
            raise ConversationError(
                message="当前会话没有可摘要的消息",
                detail=f"conversation_id={conversation_id}",
                status_code=400,
            )

        summarized_message_count = int(
            conversation.get("summarized_message_count") or 0
        )

        recent_start_index: int = max(
            len(messages) - SUMMARY_KEEP_RECENT_MESSAGES,
            0,
        )

        messages_to_summarize: list[dict[str, Any]] = messages[
            summarized_message_count:recent_start_index
        ]

        if not messages_to_summarize and conversation.get("summary"):
            return {
                "conversation_id": conversation_id,
                "summary": conversation["summary"],
                "summarized_message_count": summarized_message_count,
                "updated_at": conversation.get("summary_updated_at")
                or conversation["updated_at"],
            }

        prompt_messages = self.build_prompt(
            messages=messages_to_summarize,
            previous_summary=conversation.get("summary"),
        )

        provider = OllamaProvider()
        selected_model = model or conversation.get("model")

        response = provider.chat(
            messages=prompt_messages,
            model=selected_model,
        )

        summary = response.content.strip()
        updated_at = datetime.now().isoformat()
        total_message_count = count_messages(conversation_id)

        updated_conversation = update_conversation(
            conversation_id,
            {
                "summary": summary,
                "summarized_message_count": total_message_count,
                "summary_updated_at": updated_at,
            },
        )

        return {
            "conversation_id": conversation_id,
            "summary": updated_conversation["summary"],
            "summarized_message_count": updated_conversation.get(
                "summarized_message_count",
                total_message_count,
            ),
            "updated_at": updated_conversation.get(
                "summary_updated_at",
                updated_at,
            ),
        }
