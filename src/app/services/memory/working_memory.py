from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

# 定义 Agent 任务状态，反映当前 Agent Run 的整体进展阶段。
TaskStatus = Literal[
    "planning",  # 正在规划阶段，尚未开始执行
    "running",  # 正在执行阶段，可能在调用工具或等待工具结果
    "waiting_tool",  # 正在等待工具结果，已经调用工具但结果尚未返回
    "ready_to_answer",  # 已经准备好回答用户，但还没有生成最终回答
    "completed",  # 已经完成任务
    "failed",  # 任务执行失败
]

PlanStepStatus = Literal[
    "pending",  # 步骤待执行
    "running",  # 步骤正在执行
    "completed",  # 步骤已完成
    "skipped",  # 步骤被跳过
    "failed",  # 步骤执行失败
]


class AgentPlanStep(BaseModel):
    """Agent 显式计划步骤。

    注意：
    这是可展示、可审计的计划，不是模型隐藏思维链。
    """

    index: int
    goal: str
    status: PlanStepStatus = "pending"
    tool_name: str | None = None
    notes: str | None = None


class WorkingMemory(BaseModel):
    """当前 Agent Run 的工作记忆。

    职责：
    1. 记录当前任务状态。
    2. 给下一轮 Planner 提供结构化上下文。
    3. 给 Trace Drawer 展示 Agent 为什么这样执行。
    """

    # 当前任务目标
    goal: str | None = None

    # 当前任务状态，反映 Agent Run 的整体进展阶段。
    task_status: TaskStatus = "planning"

    # 当前 Agent 计划的步骤列表，反映 Agent 的显式计划。
    plan: list[AgentPlanStep] = Field(default_factory=list)

    # 当前任务已确认的事实，用于后续决策和回应的上下文补充。
    known_facts: list[str] = Field(default_factory=list)

    # 当前任务需要遵守的约束条件，例如时间、资源、风格、范围等。
    constraints: list[str] = Field(default_factory=list)

    # 当前任务中尚未解决的问题或疑问，用于规划下一步行动。
    open_questions: list[str] = Field(default_factory=list)

    # 结构化记忆上下文，通常是流程中生成的中间信息或外部知识片段。
    memory_context: list[dict[str, Any]] = Field(default_factory=list)

    # 从检索或外部工具获取到的补充上下文信息。
    retrieved_context: list[dict[str, Any]] = Field(default_factory=list)

    # 工具调用过程中的观测结果，用于追踪和解释 Agent 决策。
    tool_observations: list[dict[str, Any]] = Field(default_factory=list)

    # 额外元数据，可存储其他与当前工作记忆相关的辅助信息。
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_fact(self, fact: str) -> None:
        """向 known_facts 中添加一个非空且未重复的事实。"""
        fact = fact.strip()
        if fact and fact not in self.known_facts:
            self.known_facts.append(fact)

    def add_constraint(self, constraint: str) -> None:
        """向 constraints 中添加一个非空且未重复的约束。"""
        constraint = constraint.strip()
        if constraint and constraint not in self.constraints:
            self.constraints.append(constraint)

    def add_open_question(self, question: str) -> None:
        """向 open_questions 中添加一个非空且未重复的问题。"""
        question = question.strip()
        if question and question not in self.open_questions:
            self.open_questions.append(question)

    def add_tool_observation(self, observation: dict[str, Any]) -> None:
        """记录工具调用返回的观察结果。"""
        self.tool_observations.append(observation)
