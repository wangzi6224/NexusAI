import pytest

from src.app.services.agent.planner_parser import (
    PlannerDecisionParser,
    PlannerParseError,
)


def test_parse_tool_call_decision() -> None:
    decision = PlannerDecisionParser().parse(
        """
        ```json
        {
          "type": "tool_call",
          "tool_name": "search_docs",
          "arguments": {"query": "组件模板"},
          "reason": "需要检索知识库"
        }
        ```
        """
    )

    assert decision.type == "tool_call"
    assert decision.tool_name == "search_docs"
    assert decision.arguments == {"query": "组件模板"}
    assert decision.confidence == 0.7


def test_parse_final_decision() -> None:
    decision = PlannerDecisionParser().parse(
        '{"type": "final", "reason": "已有足够信息"}'
    )

    assert decision.type == "final"
    assert decision.tool_name is None
    assert decision.arguments == {}


def test_rejects_tool_call_without_tool_name() -> None:
    with pytest.raises(PlannerParseError, match="Planner decision schema invalid"):
        PlannerDecisionParser().parse(
            '{"type": "tool_call", "reason": "需要调用工具"}'
        )


def test_rejects_final_with_arguments() -> None:
    with pytest.raises(PlannerParseError, match="Planner decision schema invalid"):
        PlannerDecisionParser().parse(
            '{"type": "final", "arguments": {"query": "x"}, "reason": "完成"}'
        )
