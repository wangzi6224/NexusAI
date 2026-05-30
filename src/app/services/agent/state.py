from typing import Any, Literal
from pydantic import BaseModel, Field


class AgentObservation(BaseModel):
    # 观察来自哪个步骤
    step: int
    # 工具名称
    tool_name: str
    # 工具参数
    arguments: dict[str, Any] = Field(default_factory=dict)
    # 工具是否执行成功
    success: bool
    # 经过长度限制后的工具结果
    result: dict[str, Any] | None = None
    # 错误码
    error_code: str | None = None
    # 错误消息
    error_message: str | None = None


class AgentStep(BaseModel):
    # 当前步骤编号
    step: int
    # 步骤类型：工具调用、最终结果、最终答案或错误
    type: Literal["tool_call", "final", "final_answer", "error"]
    # 使用的工具名称（如果有）
    tool_name: str | None = None
    # 传递给工具的参数
    arguments: dict[str, Any] = Field(default_factory=dict)
    # 工具执行或步骤结果
    result: dict[str, Any] | None = None
    # 当前步骤是否成功
    success: bool = True
    # 当前步骤的延迟，单位毫秒
    latency_ms: int = 0
    # 如果失败或需要解释，则记录原因
    reason: str | None = None
    # 错误代码
    error_code: str | None = None
    # 错误消息描述
    error_message: str | None = None


class AgentState(BaseModel):
    # 运行ID
    run_id: str
    # 会话ID
    conversation_id: str
    # 用户消息ID
    user_message_id: str
    # 用户问题
    question: str
    # 消息列表
    messages: list[dict[str, Any]]
    # 步骤列表
    steps: list[AgentStep] = Field(default_factory=list)
    # 观察列表
    observations: list[AgentObservation] = Field(default_factory=list)
    # 最大步骤数
    max_steps: int = 3
    # 模型名称
    model: str
    # top_k 参数
    top_k: int = 5
    # 分数阈值
    score_threshold: float = 0.3
    # 结束原因
    finish_reason: str | None = None
