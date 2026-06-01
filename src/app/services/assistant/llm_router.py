import json
from time import perf_counter
from typing import Any

from pydantic import ValidationError

from src.app.config import resolve_llm_model
from src.app.services.assistant.llm_route_prompt import build_route_messages
from src.app.services.assistant.mode_router import RouterContext, RuleBasedModeRouter
from src.app.services.assistant.route_decision import RouteDecision
from src.app.services.llm.factory import get_llm_provider


class LLMModeRouter:
    def __init__(self) -> None:
        self.llm_provider = get_llm_provider()

    def route(self, context: RouterContext, model: str | None = None) -> RouteDecision:
        messages = build_route_messages(
            message=context.message,
            recent_messages=context.recent_messages,
            options=context.options,
        )
        selected_model = resolve_llm_model(model=model)
        start = perf_counter()

        response = self.llm_provider.chat(messages=messages, model=selected_model)
        latency_ms = int((perf_counter() - start) * 1000)

        try:
            payload = self._parse_json(response.content)
            decision = RouteDecision(
                **payload,
                source="llm",
            )
            return decision.model_copy(
                update={
                    "reason": f"{decision.reason}；llm_router_latency_ms={latency_ms}",
                }
            )
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError) as exc:
            return RouteDecision(
                mode="chat",
                confidence=0.3,
                source="fallback",
                reason=f"LLM Router 输出解析失败，降级为 chat：{type(exc).__name__}",
            )

    def _parse_json(self, content: str) -> dict[str, Any]:
        clean = content.strip()
        if clean.startswith("```"):
            clean = clean.strip("`")
            clean = clean.removeprefix("json").strip()
        return json.loads(clean)


class ModeRouter:
    def __init__(self) -> None:
        self.rule_router = RuleBasedModeRouter()
        self.llm_router = LLMModeRouter()

    def route(self, context: RouterContext, model: str | None = None) -> RouteDecision:
        rule_decision = self.rule_router.route(context)
        if rule_decision is not None:
            return rule_decision

        return self.llm_router.route(context, model=model)
