from typing import Any, Literal

from pydantic import BaseModel, Field

AgentDecisionType = Literal["tool_call", "final"]


PLANNER_DECISION_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "type": {"enum": ["tool_call", "final"]},
        "tool_name": {
            "anyOf": [
                {"type": "string", "maxLength": 80},
                {"type": "null"},
            ]
        },
        "arguments": {"type": "object"},
        "reason": {"type": "string", "minLength": 1, "maxLength": 500},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["type", "reason"],
    "allOf": [
        {
            "if": {"properties": {"type": {"const": "tool_call"}}},
            "then": {
                "required": ["tool_name"],
                "properties": {
                    "tool_name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 80,
                    },
                    "arguments": {"type": "object"},
                },
            },
        },
        {
            "if": {"properties": {"type": {"const": "final"}}},
            "then": {
                "properties": {
                    "tool_name": {"type": "null"},
                    "arguments": {"type": "object", "maxProperties": 0},
                },
            },
        },
    ],
}


class AgentDecision(BaseModel):
    """LLM Planner 每一轮的结构化决策。"""

    type: AgentDecisionType
    tool_name: str | None = Field(default=None, max_length=80)
    arguments: dict[str, Any] = Field(default_factory=dict)
    reason: str = Field(..., min_length=1, max_length=500)
    confidence: float = Field(default=0.7, ge=0, le=1)
