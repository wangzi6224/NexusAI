from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

ConversationStateSource = Literal[
    "manual",
    "assistant_auto_extract",
    "summary_refresh",
]


class ConversationState(BaseModel):
    """当前会话的结构化短期记忆。"""

    conversation_id: str

    current_goal: str | None = None
    current_topic: str | None = None

    confirmed_facts: list[str] = Field(default_factory=list)
    confirmed_constraints: list[str] = Field(default_factory=list)
    user_preferences: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)

    task_state: dict[str, Any] = Field(default_factory=dict)

    source: ConversationStateSource = "assistant_auto_extract"
    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime | None = None
    updated_at: datetime | None = None


class ConversationStatePatch(BaseModel):
    """用于更新当前会话状态的结构。"""

    current_goal: str | None = None
    current_topic: str | None = None

    confirmed_facts: list[str] | None = None
    confirmed_constraints: list[str] | None = None
    user_preferences: list[str] | None = None
    open_questions: list[str] | None = None

    task_state: dict[str, Any] | None = None
    source: ConversationStateSource = "assistant_auto_extract"
    metadata: dict[str, Any] | None = None
