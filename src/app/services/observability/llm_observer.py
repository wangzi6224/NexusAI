from __future__ import annotations

from typing import Any

from src.app.services.observability.cost import estimate_cost
from src.app.services.observability.prompt_registry import get_prompt_version
from src.app.services.observability.token_usage import build_token_usage
from src.app.services.observability.trace_schema import TokenUsage


def build_llm_span_metadata(
    *,
    operation: str,
    prompt_name: str,
    model: str,
    provider: str,
    messages: list[dict[str, str]] | None = None,
    completion_text: str | None = None,
    provider_usage: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    usage = build_token_usage(
        messages=messages,
        completion_text=completion_text,
        provider_usage=provider_usage,
    )

    cost = estimate_cost(
        model=model,
        usage=usage,
    )

    return {
        "operation": operation,
        "prompt_name": prompt_name,
        "prompt_version": get_prompt_version(prompt_name),
        "model": model,
        "provider": provider,
        "usage": usage.model_dump(mode="json"),
        "cost": cost.model_dump(mode="json"),
        **(extra or {}),
    }
