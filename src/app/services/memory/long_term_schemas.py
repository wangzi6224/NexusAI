from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

# 长期记忆类型，用于区分记忆的语义类别。
LongTermMemoryType = Literal[
    "user_profile",
    "semantic",
    "episodic",
    "tool_preference",
    "project",
]

# 长期记忆状态：active 表示可用，archived 表示归档，deleted 表示已删除。
MemoryStatus = Literal["active", "archived", "deleted"]

# 记忆来源，说明这条长期记忆是如何产生的。
MemorySource = Literal[
    "explicit_user_request",
    "assistant_auto_extract",
    "tool_observation",
    "manual",
]


class LongTermMemoryItem(BaseModel):
    """长期记忆的完整数据模型。

    该模型用于存储持久化的记忆项，包含来源、类型、内容、重要性、
    信心度、访问统计以及元数据等信息。
    """

    id: str

    user_id: str = "default_user"
    workspace_id: str | None = None

    conversation_id: str | None = None
    source_message_id: str | None = None
    source_run_id: str | None = None

    memory_type: LongTermMemoryType

    content: str = Field(min_length=1, max_length=2000)
    normalized_content: str | None = None

    importance: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)

    access_count: int = 0
    last_accessed_at: datetime | None = None

    expires_at: datetime | None = None
    status: MemoryStatus = "active"

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime | None = None
    updated_at: datetime | None = None


# 增
class LongTermMemoryCreate(BaseModel):
    """创建长期记忆的请求模型。

    用于向长期记忆存储中写入新记忆，包含必要的上下文关联和内容信息。
    """

    user_id: str = "default_user"
    workspace_id: str | None = None

    conversation_id: str | None = None
    source_message_id: str | None = None
    source_run_id: str | None = None

    memory_type: LongTermMemoryType
    content: str = Field(min_length=1, max_length=2000)

    importance: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)

    expires_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# 改
class LongTermMemoryUpdate(BaseModel):
    """更新长期记忆的请求模型。

    用于修改已有记忆的内容、重要性、置信度、状态、过期时间或元数据。
    """

    content: str | None = Field(default=None, min_length=1, max_length=2000)
    importance: float | None = Field(default=None, ge=0, le=1)
    confidence: float | None = Field(default=None, ge=0, le=1)
    status: MemoryStatus | None = None
    expires_at: datetime | None = None
    metadata: dict[str, Any] | None = None


# 查
class LongTermMemorySearchRequest(BaseModel):
    """长期记忆检索请求模型。

    用于根据用户查询从长期记忆中搜索相关记忆项，支持类型过滤、数量限制和最小相似度阈值。
    """

    query: str = Field(..., min_length=1)

    user_id: str = "default_user"
    workspace_id: str | None = None

    memory_types: list[LongTermMemoryType] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)
    min_score: float = Field(default=0.25, ge=0, le=1)


# 查
class RetrievedLongTermMemory(BaseModel):
    """长期记忆检索结果项。

    包含被检索出的记忆、相似度分数、排序名次及检索原因说明。
    """

    item: LongTermMemoryItem
    score: float = Field(ge=0, le=1)
    rank: int
    reason: str | None = None


class LongTermMemoryRetrievalResult(BaseModel):
    """长期记忆检索结果集合。

    包含检索请求、命中记忆项列表、耗时指标与可选的 trace 信息。
    """

    query: str
    items: list[RetrievedLongTermMemory]
    latency_ms: int
    trace: dict[str, Any] = Field(default_factory=dict)


class ExtractedLongTermMemoryCandidate(BaseModel):
    """候选长期记忆提取项。

    该模型用于从对话或工具结果中自动抽取潜在长期记忆，
    并在写入前进行合法性校验。
    """

    memory_type: LongTermMemoryType
    content: str = Field(min_length=1, max_length=1000)
    importance: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    source: MemorySource = "assistant_auto_extract"
    reason: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def validate_stable_statement(self) -> "ExtractedLongTermMemoryCandidate":
        content = self.content.strip()

        if content.endswith("?") or content.endswith("？"):
            raise ValueError(
                "长期记忆必须是一个稳定的陈述，不能是一个问题。请修改 content，使其成为一个明确的事实或信息。",
            )

        return self


class LongTermMemoryWriteResult(BaseModel):
    """长期记忆写入结果模型。

    用于返回写入过程中的创建、跳过、更新列表，以及相关 trace 信息。
    """

    created: list[LongTermMemoryItem] = Field(default_factory=list)
    skipped: list[dict[str, Any]] = Field(default_factory=list)
    updated: list[LongTermMemoryItem] = Field(default_factory=list)
    trace: dict[str, Any] = Field(default_factory=dict)
