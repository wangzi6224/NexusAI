from __future__ import annotations

import json
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

from src.app.services.agent.decision_schema import (
    PLANNER_DECISION_SCHEMA,
    AgentDecision,
)


class PlannerParseError(ValueError):
    pass


class PlannerDecisionParser:
    """解析 LLM 输出的决策 JSON，并进行 schema 和模型校验。"""

    _validator = Draft202012Validator(PLANNER_DECISION_SCHEMA)

    def parse(self, content: str) -> AgentDecision:
        """解析 LLM 输出的决策 JSON，并进行 schema 和模型校验。"""
        payload = self._load_json(content)
        try:
            self._validator.validate(payload)
        except ValidationError as exc:
            path = f" at {exc.json_path}" if exc.json_path != "$" else ""
            raise PlannerParseError(
                f"Planner decision schema invalid{path}: {exc.message}"
            ) from exc

        try:
            return AgentDecision.model_validate(payload)
        except Exception as exc:
            raise PlannerParseError(f"Planner decision model invalid: {exc}") from exc

    def _load_json(self, content: str) -> dict[str, Any]:
        """尝试从文本中提取 JSON 对象，支持纯 JSON 或者包含 JSON 的文本。"""
        clean = content.strip()

        if clean.startswith("```"):
            clean = clean.strip("`").strip()
            if clean.startswith("json"):
                clean = clean.removeprefix("json").strip()

        try:
            value = json.loads(clean)
        except json.JSONDecodeError:
            value = self._try_extract_json_object(clean)

        if not isinstance(value, dict):
            raise PlannerParseError("Planner output must be a JSON object")

        return value

    def _try_extract_json_object(self, text: str) -> dict[str, Any]:
        """尝试从文本中提取第一个 JSON 对象，适用于模型输出中包含解释文字的情况。"""
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise PlannerParseError("No JSON object found in planner output")

        raw = text[start : end + 1]
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise PlannerParseError(f"Invalid JSON object: {exc}") from exc

        if not isinstance(value, dict):
            raise PlannerParseError("Extracted JSON is not an object")

        return value
