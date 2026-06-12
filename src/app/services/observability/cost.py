from __future__ import annotations

from src.app.services.observability.trace_schema import CostUsage, TokenUsage

MODEL_PRICE_TABLE: dict[str, dict[str, float]] = {
    # 单位：每 1M tokens 的美元价格。这里只做示例。
    "default": {
        "input_per_1m": 0.0,
        "output_per_1m": 0.0,
    },
    "deepseek-chat": {
        "input_per_1m": 0.27,
        "output_per_1m": 1.10,
    },
    "qwen-plus": {
        "input_per_1m": 0.30,
        "output_per_1m": 0.60,
    },
}


def estimate_cost(
    *,
    model: str,
    usage: TokenUsage,
    currency: str = "USD",
) -> CostUsage:
    price = MODEL_PRICE_TABLE.get(model) or MODEL_PRICE_TABLE["default"]

    prompt_cost = usage.prompt_tokens / 1_000_000 * price["input_per_1m"]
    completion_cost = usage.completion_tokens / 1_000_000 * price["output_per_1m"]

    return CostUsage(
        currency=currency,
        prompt_cost=round(prompt_cost, 8),
        completion_cost=round(completion_cost, 8),
        total_cost=round(prompt_cost + completion_cost, 8),
        estimated=True,
    )
