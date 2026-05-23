# src/app/services/agent/loop.py
from time import perf_counter
from typing import Any

from src.app.services.agent.state import AgentState, AgentStep
from src.app.services.agent.planner import RuleBasedPlanner
from src.app.services.tools.registry import ToolRegistry


class AgentLoop:
    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry
        self.planner = RuleBasedPlanner()

    def run(self, state: AgentState) -> AgentState:
        for index in range(state.max_steps):
            decision = self.planner.plan(
                question=state.question,
                step_count=len(state.steps),
            )

            if decision["type"] == "final":
                state.steps.append(
                    AgentStep(
                        step=index + 1,
                        type="final",
                        reason=decision.get("reason"),
                    )
                )
                return state

            tool_name = decision["tool_name"]
            arguments = decision.get("arguments", {})

            start = perf_counter()

            try:
                tool = self.tool_registry.get(tool_name)
                result = tool.run(arguments)
                latency_ms = int((perf_counter() - start) * 1000)

                state.steps.append(
                    AgentStep(
                        step=index + 1,
                        type="tool_call",
                        tool_name=tool_name,
                        arguments=arguments,
                        result=result,
                        success=bool(result.get("success")),
                        latency_ms=latency_ms,
                        reason=decision.get("reason"),
                    )
                )

                # 第一版：调用一次工具后就结束，避免重复调用同一个工具。
                return state

            except Exception as exc:
                latency_ms = int((perf_counter() - start) * 1000)

                state.steps.append(
                    AgentStep(
                        step=index + 1,
                        type="tool_call",
                        tool_name=tool_name,
                        arguments=arguments,
                        result={
                            "success": False,
                            "error": {
                                "code": "TOOL_EXECUTION_ERROR",
                                "message": str(exc),
                            },
                        },
                        success=False,
                        latency_ms=latency_ms,
                        reason=decision.get("reason"),
                    )
                )

                return state

        return state
