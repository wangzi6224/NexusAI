import json
from time import perf_counter
from typing import Any

from pydantic import ValidationError

from src.app.logger import get_logger
from src.app.config import get_llm_router_model
from src.app.services.assistant.llm_route_prompt import build_route_messages
from src.app.services.assistant.mode_router import RouterContext, RuleBasedModeRouter
from src.app.services.assistant.route_decision import RouteDecision
from src.app.services.llm.factory import get_llm_provider

logger = get_logger()


class LLMModeRouter:
    def __init__(self) -> None:
        self.llm_provider = get_llm_provider()

    def route(self, context: RouterContext, model: str | None = None) -> RouteDecision:

        # 构建提示词和消息列表，调用 LLM 进行路由决策，并解析输出。
        messages = build_route_messages(
            message=context.message,
            recent_messages=context.recent_messages,
            options=context.options,
        )
        llm_router_model = get_llm_router_model()
        start = perf_counter()

        logger.info(
            "LLM Router 开始路由决策，model=%s, message=%s",
            llm_router_model,
            context.message,
        )
        # 这里直接调用 LLM 进行路由决策
        response = self.llm_provider.structured_chat(
            messages=messages, model=llm_router_model, thinking_enabled=False
        )
        latency_ms = int((perf_counter() - start) * 1000)

        logger.info(
            "LLM Router 路由决策完成，model=%s 耗时 %s ms，响应内容: %s",
            llm_router_model,
            latency_ms,
            response.content,
        )

        try:
            payload = self._parse_json(response.content)
            if payload.get("mode") == "rag":
                payload["mode"] = "agent"
                reason = (
                    f"{payload.get('reason') or '知识库请求'}；"
                    "知识库请求通过 Agent tools 执行"
                )
                payload["reason"] = reason[:300]
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
        # 先通过规则路由，如果规则无法确定则调用 LLM 路由。
        rule_decision = self.rule_router.route(context)
        if rule_decision is not None:
            return rule_decision

        return self.llm_router.route(context, model=model)
