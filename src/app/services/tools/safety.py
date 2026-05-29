from __future__ import annotations

import json
from typing import Any

from src.app.config import get_agent_max_tool_result_chars


def limit_tool_result(result: dict[str, Any]) -> dict[str, Any]:
    max_chars = get_agent_max_tool_result_chars()
    text = json.dumps(result, ensure_ascii=False)

    if len(text) <= max_chars:
        return result

    return {
        "success": result.get("success", False),
        "data": {
            "truncated": True,
            "preview": text[:max_chars],
        },
        "error": result.get("error"),
        "metadata": {
            **(result.get("metadata") or {}),
            "truncated": True,
            "original_chars": len(text),
            "max_chars": max_chars,
        },
    }
