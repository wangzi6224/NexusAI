from __future__ import annotations

from time import perf_counter
from typing import Any

from jsonschema import ValidationError

from src.app.agent_trace_store import create_agent_event
from src.app.config import resolve_llm_model
from src.app.services.agent.decision_schema import AgentDecision
from src.app.services.agent.planner import RuleBasedPlanner
from src.app.services.agent.planner_parser import PlannerDecisionParser
from src.app.services.agent.planner_prompt_builder import LLMPlannerPromptBuilder
from src.app.services.agent.state import AgentState
from src.app.services.assistant.event import (
    EVENT_PLANNER_DECISION,
    EVENT_PLANNER_FALLBACK,
)
from src.app.services.llm.factory import get_llm_provider
from src.app.services.tools.registry import ToolRegistry


class LLMPlanner:
    """LLM Planner。

    注意：
    - 模型只给决策建议；
    - 代码层负责 schema 校验、工具白名单、参数校验和 fallback；
    - 任何异常都不能让 Agent 直接 500。
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry
        self.llm_provider = get_llm_provider()
        self.prompt_builder = LLMPlannerPromptBuilder()
        self.parser = PlannerDecisionParser()
        self.fallback_planner = RuleBasedPlanner()

    def plan(self, state: AgentState) -> dict[str, Any]:
        start = perf_counter()
        tools = self.tool_registry.list_tools()
        messages = self.prompt_builder.build_messages(state=state, tools=tools)
        selected_model = resolve_llm_model(model=state.model)

        try:
            response = self.llm_provider.structured_chat(
                messages=messages, model=selected_model
            )
            decision = self.parser.parse(response.content)
            decision = self._validate_decision(state=state, decision=decision)

            latency_ms = int((perf_counter() - start) * 1000)
            create_agent_event(
                run_id=state.run_id,
                event_type=EVENT_PLANNER_DECISION,
                payload={
                    "planner": "llm",
                    "decision": decision.model_dump(),
                    "latency_ms": latency_ms,
                    "model": response.model,
                    "provider": response.provider,
                },
            )
            return decision.model_dump()

        except Exception as exc:
            latency_ms = int((perf_counter() - start) * 1000)
            fallback = self.fallback_planner.plan(state)
            state.planner_fallback_count += 1
            create_agent_event(
                run_id=state.run_id,
                event_type=EVENT_PLANNER_FALLBACK,
                payload={
                    "planner": "llm",
                    "fallback_planner": "rule_based",
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "latency_ms": latency_ms,
                    "fallback_decision": fallback,
                },
            )
            return fallback

    def _validate_decision(
        self,
        *,
        state: AgentState,
        decision: AgentDecision,
    ) -> AgentDecision:
        if decision.type == "final":
            return decision

        assert decision.tool_name is not None

        # 1. ToolRegistry 会做白名单和注册校验。
        self.tool_registry.get(decision.tool_name)

        # 2. 参数 schema 校验。
        try:
            self.tool_registry.validate_arguments(
                decision.tool_name, decision.arguments
            )
        except ValidationError as exc:
            raise ValueError(
                f"Planner generated invalid tool arguments: {exc.message}"
            ) from exc

        # 3. 业务层重复调用校验。
        for step in state.steps:
            if step.type != "tool_call":
                continue
            if (
                step.tool_name == decision.tool_name
                and step.arguments == decision.arguments
            ):
                raise ValueError("Planner generated duplicate tool call")

        return decision
