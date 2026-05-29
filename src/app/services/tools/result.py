from __future__ import annotations

from typing import Any


def tool_success(
    *,
    tool_name: str,
    data: dict[str, Any],
    latency_ms: int = 0,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "error": None,
        "metadata": {
            "tool_name": tool_name,
            "latency_ms": latency_ms,
            **(metadata or {}),
        },
    }


def tool_error(
    *,
    tool_name: str,
    code: str,
    message: str,
    latency_ms: int = 0,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
        },
        "metadata": {
            "tool_name": tool_name,
            "latency_ms": latency_ms,
            **(metadata or {}),
        },
    }
