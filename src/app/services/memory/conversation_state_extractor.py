from __future__ import annotations

import json
from typing import Any

from pydantic import TypeAdapter, ValidationError

from src.app.services.llm.factory import get_llm_provider
from src.app.services.memory.short_term_schemas import ConversationStatePatch

CONVERSATION_STATE_PROMPT_VERSION = "conversation_state_v1"

CONVERSATION_STATE_SYSTEM_PROMPT = """
你是 NexusAI 的 Conversation State Extractor。

你的任务是维护当前会话的结构化短期状态。
这不是长期记忆，不要保存跨会话偏好。

请从当前用户输入、助手回答和已有 state 中提取：
1. current_goal：当前会话正在完成的主要目标。
2. current_topic：当前正在讨论的主题。
3. confirmed_facts：当前会话内明确确认的事实。
4. confirmed_constraints：当前任务必须遵守的约束。
5. user_preferences：当前会话内用户表达的偏好。
6. open_questions：仍待解决的问题。
7. task_state：适合用 JSON 表达的当前任务进度。

要求：
- 只基于原文，不要推断。
- 不要保存 API key、token、密码、隐私敏感信息。
- 不要把长期偏好写到这里作为跨会话记忆。
- 输出 JSON 对象，不要输出 Markdown。
"""


class ConversationStateExtractor:
    def __init__(self) -> None:
        self.llm_provider = get_llm_provider()
        self.adapter = TypeAdapter(ConversationStatePatch)

    def extract(
        self,
        *,
        user_message: str,
        assistant_answer: str,
        previous_state: dict[str, Any] | None,
        model: str | None = None,
    ) -> ConversationStatePatch:
        messages = [
            {
                "role": "system",
                "content": CONVERSATION_STATE_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "请更新当前会话短期状态。\n\n"
                    f"已有 state：\n{json.dumps(previous_state or {}, ensure_ascii=False)}\n\n"
                    f"用户输入：\n{user_message}\n\n"
                    f"助手回答：\n{assistant_answer}\n"
                ),
            },
        ]

        response = self.llm_provider.structured_chat(messages=messages, model=model)

        print(json.dumps(response.content, ensure_ascii=False, indent=2))  # 调试输出

        try:
            payload = self._parse_json(response.content)
            patch = self.adapter.validate_python(payload)
            patch.metadata = {
                **(patch.metadata or {}),
                "prompt_version": CONVERSATION_STATE_PROMPT_VERSION,
                "extractor": "llm",
                "fallback": False,
            }
            return patch
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
            return ConversationStatePatch(
                metadata={
                    "prompt_version": CONVERSATION_STATE_PROMPT_VERSION,
                    "extractor": "llm",
                    "fallback": True,
                }
            )

    def _parse_json(self, content: str) -> Any:
        clean = content.strip()

        if clean.startswith("```"):
            clean = clean.strip("`")
            clean = clean.removeprefix("json").strip()

        return json.loads(clean)
