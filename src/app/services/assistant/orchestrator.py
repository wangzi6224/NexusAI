from __future__ import annotations

from collections.abc import Iterable
from time import perf_counter
from typing import Any

from src.app.config import resolve_llm_model
from src.app.conversation_store import (
    create_message,
    get_conversation,
    update_conversation,
)
from src.app.exceptions import ConversationError
from src.app.logger import get_logger
from src.app.schemas.assistant import AssistantStreamRequest, RouteDecision
from src.app.services.agent.agent_service import AgentService
from src.app.services.assistant.event import sse_event
from src.app.services.assistant.mode_router import ModeRouter
from src.app.services.assistant.run_store import AssistantRunStore
from src.app.services.context_builder import ContextBuilder
from src.app.services.llm.factory import get_llm_provider
from src.app.services.summarizer import Summarizer

logger = get_logger()


class AssistantOrchestrator:
    """统一 Assistant 入口编排器。

    Week 14 Agent-first 版本：
    - mode=chat：普通多轮聊天
    - mode=agent：工具增强聊天，包括知识库检索
    - mode=auto：规则路由到 chat 或 agent

    注意：这里没有 mode=rag。
    RAG 能力通过 Agent tools 使用。
    """

    def __init__(self) -> None:
        self.mode_router = ModeRouter()
        self.run_store = AssistantRunStore()
        self.agent_service = AgentService()

    def stream(
        self,
        *,
        conversation_id: str,
        request: AssistantStreamRequest,
    ) -> Iterable[str]:
        start = perf_counter()
        clean_message = request.message.strip()

        if not clean_message:
            # 消息内容不能为空，直接返回错误事件并结束流。
            yield sse_event(
                "error",
                {
                    "code": "EMPTY_MESSAGE",
                    "message": "消息内容不能为空",
                },
            )
            yield sse_event("done", "[DONE]")
            return

        conversation = get_conversation(conversation_id)
        if conversation is None:
            # 会话不存在，直接返回错误事件并结束流。
            yield sse_event(
                "error",
                {
                    "code": "CONVERSATION_NOT_FOUND",
                    "message": "会话不存在",
                    "detail": f"conversation_id={conversation_id}",
                },
            )
            yield sse_event("done", "[DONE]")
            return

        route_decision = self.mode_router.route(request)

        selected_model = resolve_llm_model(
            model=request.model,
            stored_model=conversation.get("model"),
            stored_provider=conversation.get("provider"),
            provider=request.provider,
        )

        assistant_run = self.run_store.create_run(
            conversation_id=conversation_id,
            mode=route_decision.mode,
            input_text=clean_message,
            model=selected_model,
            provider=request.provider or conversation.get("provider"),
            metadata={
                "requested_mode": request.mode,
                "options": request.options.model_dump(),
                "route_decision": route_decision.model_dump(),
            },
        )
        assistant_run_id = assistant_run["id"]

        yield sse_event(
            "assistant_start",
            {
                "assistant_run_id": assistant_run_id,
                "conversation_id": conversation_id,
                "mode": route_decision.mode,
                "requested_mode": request.mode,
            },
        )

        yield sse_event(
            "route_decision",
            {
                "mode": route_decision.mode,
                "reason": route_decision.reason,
                "matched_keywords": route_decision.matched_keywords,
            },
        )

        try:
            if route_decision.mode == "chat":
                yield from self._stream_chat(
                    conversation_id=conversation_id,
                    clean_message=clean_message,
                    selected_model=selected_model,
                    provider=request.provider,
                    assistant_run_id=assistant_run_id,
                    route_decision=route_decision,
                    start=start,
                )
                return

            yield from self._stream_agent(
                conversation_id=conversation_id,
                clean_message=clean_message,
                selected_model=selected_model,
                assistant_run_id=assistant_run_id,
                request=request,
                route_decision=route_decision,
                start=start,
            )

        except Exception as exc:
            latency_ms = int((perf_counter() - start) * 1000)
            logger.exception(
                "Assistant stream failed: conversation_id=%s run_id=%s error=%s",
                conversation_id,
                assistant_run_id,
                exc,
            )

            self.run_store.update_run(
                assistant_run_id,
                status="failed",
                latency_ms=latency_ms,
                trace={
                    "error": {
                        "code": "ASSISTANT_STREAM_ERROR",
                        "message": str(exc),
                    },
                    "route_decision": route_decision.model_dump(),
                },
            )

            yield sse_event(
                "error",
                {
                    "code": "ASSISTANT_STREAM_ERROR",
                    "message": "Assistant 处理失败",
                    "detail": str(exc),
                },
            )
            yield sse_event("done", "[DONE]")

    def _stream_chat(
        self,
        *,
        conversation_id: str,
        clean_message: str,
        selected_model: str,
        provider: str | None,
        assistant_run_id: str,
        route_decision: RouteDecision,
        start: float,
    ) -> Iterable[str]:
        user_message = create_message(
            conversation_id=conversation_id,
            role="user",
            content=clean_message,
            metadata={
                "type": "assistant_user_message",
                "assistant_run_id": assistant_run_id,
                "mode": "chat",
            },
        )

        context_builder = ContextBuilder()
        llm_messages = context_builder.build_messages(conversation_id)

        llm_provider = get_llm_provider(provider)
        full_answer_parts: list[str] = []

        for chunk in llm_provider.stream_chat(
            message=llm_messages,
            model=selected_model,
        ):
            if chunk.done:
                break

            full_answer_parts.append(chunk.delta)
            yield sse_event("delta", {"delta": chunk.delta})

        full_answer = "".join(full_answer_parts)
        latency_ms = int((perf_counter() - start) * 1000)

        assistant_message = create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_answer,
            metadata={
                "type": "assistant_answer",
                "assistant_run_id": assistant_run_id,
                "mode": "chat",
                "model": selected_model,
                "provider": llm_provider.name,
                "latency_ms": latency_ms,
                "context_message_count": len(llm_messages),
                "is_stream": True,
                "tool_calls": [],
                "trace": {
                    "route_decision": route_decision.model_dump(),
                    "context_message_count": len(llm_messages),
                },
            },
        )

        self._try_update_summary(conversation_id, model=selected_model)

        update_conversation(
            conversation_id,
            {
                "model": selected_model,
                "provider": llm_provider.name,
            },
        )

        trace = {
            "assistant_run_id": assistant_run_id,
            "mode": "chat",
            "route_decision": route_decision.model_dump(),
            "context_message_count": len(llm_messages),
            "tool_calls": [],
        }

        self.run_store.update_run(
            assistant_run_id,
            status="completed",
            user_message_id=user_message["id"],
            assistant_message_id=assistant_message["id"],
            final_answer=full_answer,
            model=selected_model,
            provider=llm_provider.name,
            latency_ms=latency_ms,
            trace=trace,
        )

        yield sse_event(
            "assistant_end",
            {
                "assistant_run_id": assistant_run_id,
                "assistant_message_id": assistant_message["id"],
                "mode": "chat",
                "latency_ms": latency_ms,
                "model": selected_model,
                "provider": llm_provider.name,
                "tool_calls": [],
                "trace": trace,
            },
        )
        yield sse_event("done", "[DONE]")

    def _stream_agent(
        self,
        *,
        conversation_id: str,
        clean_message: str,
        selected_model: str,
        assistant_run_id: str,
        request: AssistantStreamRequest,
        route_decision: RouteDecision,
        start: float,
    ) -> Iterable[str]:
        # 当前 AgentService.chat 是同步执行。
        # Week 14 先统一 SSE 协议，不强行改 AgentLoop 为流式。
        result = self.agent_service.chat(
            conversation_id=conversation_id,
            question=clean_message,
            top_k=request.options.top_k,
            score_threshold=request.options.score_threshold,
            max_steps=request.options.max_steps,
            model=selected_model,
        )

        tool_calls = result.get("tool_calls", [])
        trace = result.get("trace", {})
        answer = result.get("answer", "")
        agent_run_id = result.get("run_id")

        for tool_call in tool_calls:
            yield sse_event(
                "tool_call_start",
                {
                    "tool_name": tool_call.get("tool_name"),
                    "arguments": tool_call.get("arguments") or {},
                    "reason": tool_call.get("reason"),
                    "step": tool_call.get("step"),
                },
            )
            yield sse_event(
                "tool_call_end",
                {
                    "tool_name": tool_call.get("tool_name"),
                    "success": tool_call.get("success"),
                    "latency_ms": tool_call.get("latency_ms"),
                    "step": tool_call.get("step"),
                    "error_code": tool_call.get("error_code"),
                    "error_message": tool_call.get("error_message"),
                },
            )

        # 第一版可以一次性返回完整答案。
        # 后续再把 Agent final answer 改成真正 token 流。
        yield sse_event("delta", {"delta": answer})

        latency_ms = int((perf_counter() - start) * 1000)

        assistant_trace: dict[str, Any] = {
            "assistant_run_id": assistant_run_id,
            "mode": "agent",
            "route_decision": route_decision.model_dump(),
            "agent_run_id": agent_run_id,
            "agent_trace": trace,
            "tool_calls": tool_calls,
        }

        # AgentService 已经保存 user/assistant message。
        # 这里无法直接拿到 assistant_message_id，因为当前 AgentService 返回值没有带。
        # Week 14 可以先记录 agent_run_id。下一步建议让 AgentService.chat 返回 user_message_id / assistant_message_id。
        self.run_store.update_run(
            assistant_run_id,
            status="completed",
            final_answer=answer,
            model=trace.get("model") or selected_model,
            provider=trace.get("provider"),
            latency_ms=latency_ms,
            trace=assistant_trace,
            metadata={
                "agent_run_id": agent_run_id,
                "tool_call_count": len(tool_calls),
            },
        )

        yield sse_event(
            "assistant_end",
            {
                "assistant_run_id": assistant_run_id,
                "agent_run_id": agent_run_id,
                "mode": "agent",
                "latency_ms": latency_ms,
                "model": trace.get("model") or selected_model,
                "provider": trace.get("provider"),
                "tool_calls": tool_calls,
                "trace": assistant_trace,
            },
        )
        yield sse_event("done", "[DONE]")

    def _try_update_summary(
        self, conversation_id: str, model: str | None = None
    ) -> None:
        try:
            summarizer = Summarizer()
            if summarizer.should_update(conversation_id):
                summarizer.summarize(conversation_id=conversation_id, model=model)
        except Exception as exc:
            logger.exception(
                "Assistant 自动更新摘要失败: conversation_id=%s error=%s",
                conversation_id,
                exc,
            )
