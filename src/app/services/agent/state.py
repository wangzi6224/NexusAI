from typing import Any, Literal
from pydantic import BaseModel, Field


class AgentStep(BaseModel):
    step: int  # 当前步骤编号
    type: Literal["tool_call", "final"]  # 步骤类型，例如 tool_call 或 final
    tool_name: str | None = None  # 调用的工具名称（如果有）
    arguments: dict[str, Any] = Field(default_factory=dict)  # 传给工具的参数
    result: dict[str, Any] | None = None  # 工具执行结果
    success: bool = True  # 该步骤是否成功
    latency_ms: int = 0  # 工具执行耗时（毫秒）
    reason: str | None = None  # 该步骤的原因或解释


class AgentState(BaseModel):
    conversation_id: str  # 会话 ID
    user_message_id: str  # 用户消息 ID
    question: str  # 用户当前提问内容
    messages: list[dict[str, Any]]  # 历史消息列表
    steps: list[AgentStep] = Field(default_factory=list)  # agent 执行过的步骤记录
    max_steps: int = 3  # 最大执行步数限制
    model: str  # 使用的模型标识
    top_k: int = 5  # 相似度检索时的 top_k
    score_threshold: float = 0.3  # 检索结果评分阈值
