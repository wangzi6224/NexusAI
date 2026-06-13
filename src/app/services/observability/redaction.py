from __future__ import annotations

from typing import Any

SENSITIVE_KEYS = {
    "authorization",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "cookie",
    "set-cookie",
    "x-api-key",
}


def redact_value(value: Any, *, max_text_chars: int = 2000) -> Any:
    """脱敏和截断 trace 中的值。"""

    if isinstance(value, dict):
        return redact_dict(value, max_text_chars=max_text_chars)

    if isinstance(value, list):
        return [
            redact_value(item, max_text_chars=max_text_chars) for item in value[:50]
        ]

    if isinstance(value, str):
        if len(value) > max_text_chars:
            return value[:max_text_chars] + "...[truncated]"
        return value

    return value


def redact_dict(
    data: dict[str, Any],
    *,
    max_text_chars: int = 2000,
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for key, value in data.items():
        normalized_key = key.lower().replace("-", "_")

        if normalized_key in SENSITIVE_KEYS:
            result[key] = "[REDACTED]"
            continue

        if any(sensitive in normalized_key for sensitive in SENSITIVE_KEYS):
            result[key] = "[REDACTED]"
            continue

        result[key] = redact_value(value, max_text_chars=max_text_chars)

    return result
