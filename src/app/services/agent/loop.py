from time import perf_counter
from src.app.services.tools.safety import limit_tool_result

from src.app.agent_trace_store import create_agent_event, create_agent_step
from src.app.services.agent.state import AgentState, AgentStep
from src.app.services.agent.planner import RuleBasedPlanner
from src.app.services.tools.registry import ToolRegistry


class AgentLoop:
    def __init__(self, tool_registry: ToolRegistry) -> None:
        # 初始化 agent 循环，注入工具注册表和规则规划器
        self.tool_registry = tool_registry
        self.planner = RuleBasedPlanner()

    def run(self, state: AgentState) -> AgentState:
        # 运行 agent 循环，最多执行 state.max_steps 个步骤
        for index in range(state.max_steps):
            step_index = index + 1
            decision = self.planner.plan(
                question=state.question,
                step_count=len(state.steps),
            )

            # 如果规划器返回 final 类型，则标记为完成并结束
            if decision["type"] == "final":
                step = AgentStep(
                    step=step_index,
                    type="final",
                    reason=decision.get("reason"),
                )
                state.steps.append(step)

                create_agent_step(
                    run_id=state.run_id,
                    step_index=step_index,
                    step_type="final",
                    reason=step.reason,
                    success=True,
                )

                create_agent_event(
                    run_id=state.run_id,
                    event_type="agent_step_final",
                    payload={
                        "step_index": step_index,
                        "reason": step.reason,
                    },
                )

                return state

            tool_name = decision["tool_name"]
            arguments = decision.get("arguments", {})

            # 记录工具调用开始事件
            create_agent_event(
                run_id=state.run_id,
                event_type="agent_step_start",
                payload={
                    "step_index": step_index,
                    "step_type": "tool_call",
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "reason": decision.get("reason"),
                },
            )

            start = perf_counter()

            try:
                tool = self.tool_registry.get(tool_name)
                result = tool.run(arguments)
                result = limit_tool_result(result)
                latency_ms = int((perf_counter() - start) * 1000)
                success = bool(result.get("success"))

                # 构造 tool_call 步骤并保存结果
                step = AgentStep(
                    step=step_index,
                    type="tool_call",
                    tool_name=tool_name,
                    arguments=arguments,
                    result=result,
                    success=success,
                    latency_ms=latency_ms,
                    reason=decision.get("reason"),
                )
                state.steps.append(step)

                create_agent_step(
                    run_id=state.run_id,
                    step_index=step_index,
                    step_type="tool_call",
                    reason=decision.get("reason"),
                    tool_name=tool_name,
                    tool_arguments=arguments,
                    tool_result=result,
                    success=success,
                    latency_ms=latency_ms,
                    error_code=(result.get("error") or {}).get("code"),
                    error_message=(result.get("error") or {}).get("message"),
                )

                create_agent_event(
                    run_id=state.run_id,
                    event_type="tool_result",
                    payload={
                        "step_index": step_index,
                        "tool_name": tool_name,
                        "success": success,
                        "latency_ms": latency_ms,
                    },
                )

                return state

            except Exception as exc:
                latency_ms = int((perf_counter() - start) * 1000)
                result = {
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "TOOL_EXECUTION_ERROR",
                        "message": str(exc),
                    },
                    "metadata": {
                        "tool_name": tool_name,
                        "latency_ms": latency_ms,
                    },
                }

                # 如果工具执行失败，则记录失败步骤和错误事件
                step = AgentStep(
                    step=step_index,
                    type="tool_call",
                    tool_name=tool_name,
                    arguments=arguments,
                    result=result,
                    success=False,
                    latency_ms=latency_ms,
                    reason=decision.get("reason"),
                    error_code="TOOL_EXECUTION_ERROR",
                    error_message=str(exc),
                )
                state.steps.append(step)

                create_agent_step(
                    run_id=state.run_id,
                    step_index=step_index,
                    step_type="tool_call",
                    reason=decision.get("reason"),
                    tool_name=tool_name,
                    tool_arguments=arguments,
                    tool_result=result,
                    success=False,
                    latency_ms=latency_ms,
                    error_code="TOOL_EXECUTION_ERROR",
                    error_message=str(exc),
                )

                create_agent_event(
                    run_id=state.run_id,
                    event_type="tool_error",
                    payload={
                        "step_index": step_index,
                        "tool_name": tool_name,
                        "latency_ms": latency_ms,
                        "error": result["error"],
                    },
                )

                return state

        # 达到最大步骤数，记录事件并返回当前状态
        create_agent_event(
            run_id=state.run_id,
            event_type="agent_max_steps_reached",
            payload={"max_steps": state.max_steps},
        )

        return state
