from typing import Any, Literal
from pydantic import BaseModel, Field


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
    # 运行 ID，用于唯一标识本次代理执行
    run_id: str
    # 会话 ID，用于关联当前会话
    conversation_id: str
    # 用户消息 ID，用于关联用户请求
    user_message_id: str
    # 用户提问内容
    question: str
    # 与当前代理执行关联的消息列表
    messages: list[dict[str, Any]]
    # 当前执行步骤列表
    steps: list[AgentStep] = Field(default_factory=list)
    # 最大步骤数
    max_steps: int = 3
    # 使用的模型名称
    model: str
    # 结果候选数量
    top_k: int = 5
    # 结果过滤分数阈值
    score_threshold: float = 0.3
