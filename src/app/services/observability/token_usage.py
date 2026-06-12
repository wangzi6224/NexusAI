from __future__ import annotations

from src.app.services.observability.trace_schema import TokenUsage


def estimate_tokens_from_text(text: str) -> int:
    """粗略 token 估算。

    中文、英文、代码混合场景下，第一版用字符数 / 2 做保守估算。
    """

    if not text:
        return 0

    return max(1, len(text) // 2)


def estimate_tokens_from_messages(messages: list[dict[str, str]]) -> int:
    total = 0

    for message in messages:
        total += estimate_tokens_from_text(message.get("content", ""))

    return total


def build_token_usage(
    *,
    prompt_text: str | None = None,
    completion_text: str | None = None,
    messages: list[dict[str, str]] | None = None,
    provider_usage: dict | None = None,
) -> TokenUsage:
    """统一构造 TokenUsage。优先使用 provider 返回的 usage。"""

    if provider_usage:
        prompt_tokens = int(provider_usage.get("prompt_tokens") or 0)
        completion_tokens = int(provider_usage.get("completion_tokens") or 0)
        total_tokens = int(
            provider_usage.get("total_tokens") or prompt_tokens + completion_tokens
        )
        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    prompt_tokens = 0

    if messages is not None:
        prompt_tokens = estimate_tokens_from_messages(messages)
    elif prompt_text is not None:
        prompt_tokens = estimate_tokens_from_text(prompt_text)

    completion_tokens = estimate_tokens_from_text(completion_text or "")

    return TokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )
