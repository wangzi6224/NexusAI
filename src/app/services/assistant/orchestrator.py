from __future__ import annotations

from collections.abc import Iterable
from time import perf_counter
from typing import Any

from src.app.config import resolve_llm_model
from src.app.conversation_store import (
    create_message,
    get_conversation,
    list_recent_messages,
    update_conversation,
)
from src.app.logger import get_logger
from src.app.schemas.assistant import AssistantStreamRequest
from src.app.services.agent.agent_service import AgentService
from src.app.services.assistant.event import (
    EVENT_ASSISTANT_END,
    EVENT_ASSISTANT_START,
    EVENT_DELTA,
    EVENT_DONE,
    EVENT_ERROR,
    EVENT_ROUTE_DECISION,
    EVENT_TOOL_CALL_END,
    EVENT_TOOL_CALL_START,
    EVENT_LONG_TERM_MEMORY_ITEM,
    EVENT_LONG_TERM_MEMORY_RETRIEVAL_START,
    EVENT_LONG_TERM_MEMORY_WRITE,
    EVENT_SHORT_TERM_MEMORY_LOADED,
    EVENT_WORKING_MEMORY_UPDATED,
    sse_event,
)
from src.app.services.assistant.llm_router import ModeRouter
from src.app.services.assistant.mode_router import RouterContext
from src.app.services.assistant.route_decision import RouteDecision
from src.app.services.assistant.run_store import AssistantRunStore
from src.app.services.context_builder import ContextBuilder
from src.app.services.llm.factory import get_llm_provider
from src.app.services.summarizer import Summarizer
from src.app.services.memory.short_term_builder import ShortTermMemoryBuilder
from src.app.services.memory.short_term_store import ShortTermMemoryStore
from src.app.services.memory.conversation_state_extractor import (
    ConversationStateExtractor,
)
from src.app.services.memory.long_term_retriever import LongTermMemoryRetriever
from src.app.services.memory.long_term_writer import LongTermMemoryWriter
from src.app.services.memory.long_term_schemas import (
    LongTermMemoryRetrievalResult,
    LongTermMemorySearchRequest,
    LongTermMemoryWriteResult,
    RetrievedLongTermMemory,
)

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

        self.short_term_builder = ShortTermMemoryBuilder()
        self.short_term_store = ShortTermMemoryStore()
        self.conversation_state_extractor = ConversationStateExtractor()

        self.long_term_retriever = LongTermMemoryRetriever()
        self.long_term_writer = LongTermMemoryWriter()

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
                EVENT_ERROR,
                {
                    "code": "EMPTY_MESSAGE",
                    "message": "消息内容不能为空",
                },
            )
            yield sse_event(EVENT_DONE, "[DONE]")
            return

        conversation = get_conversation(conversation_id)
        if conversation is None:
            # 会话不存在，直接返回错误事件并结束流。
            yield sse_event(
                EVENT_ERROR,
                {
                    "code": "CONVERSATION_NOT_FOUND",
                    "message": "会话不存在",
                    "detail": f"conversation_id={conversation_id}",
                },
            )
            yield sse_event(EVENT_DONE, "[DONE]")
            return

        selected_model = resolve_llm_model(
            model=request.model,
            stored_model=conversation.get("model"),
            stored_provider=conversation.get("provider"),
            provider=request.provider,
        )

        try:
            route_start = perf_counter()
            route_decision = self._route(
                conversation_id=conversation_id,
                request=request,
                selected_model=selected_model,
            )
            route_ms = int((perf_counter() - route_start) * 1000)

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
        except Exception as exc:
            latency_ms = int((perf_counter() - start) * 1000)
            logger.exception(
                "Assistant route/start failed: conversation_id=%s error=%s",
                conversation_id,
                exc,
            )
            yield sse_event(
                EVENT_ERROR,
                {
                    "code": "ASSISTANT_ROUTE_ERROR",
                    "message": "Assistant 路由初始化失败",
                    "detail": str(exc),
                    "latency_ms": latency_ms,
                },
            )
            yield sse_event(EVENT_DONE, "[DONE]")
            return

        yield sse_event(
            EVENT_ASSISTANT_START,
            {
                "assistant_run_id": assistant_run_id,
                "conversation_id": conversation_id,
                "mode": route_decision.mode,
                "requested_mode": request.mode,
            },
        )

        yield sse_event(
            EVENT_ROUTE_DECISION,
            {
                "mode": route_decision.mode,
                "reason": route_decision.reason,
                "matched_keywords": route_decision.matched_keywords,
            },
        )

        short_term_memory: dict[str, Any] | None = None
        long_term_memory: LongTermMemoryRetrievalResult | None = None
        long_term_memory_items: list[RetrievedLongTermMemory] = []

        if request.options.enable_short_term_memory:
            # 构建短期记忆，供后续 Agent 使用。目前仅包含最近的对话消息，后续可以增加更多类型的记忆。
            short_term_memory = self.short_term_builder.build(
                conversation_id=conversation_id,
                recent_limit=10,
            )

        if (
            request.options.enable_long_term_memory
            and request.options.long_term_memory_top_k > 0
        ):
            # 构建长期记忆检索请求，供后续 Agent 使用。目前支持多种记忆类型的检索，后续可以增加更多选项。
            long_term_memory = self.long_term_retriever.retrieve(
                LongTermMemorySearchRequest(
                    query=clean_message,
                    user_id="default_user",
                    top_k=request.options.long_term_memory_top_k,
                    min_score=request.options.long_term_memory_min_score,
                    memory_types=[
                        "user_profile",
                        "semantic",
                        "episodic",
                        "tool_preference",
                        "project",
                    ],
                )
            )
            long_term_memory_items = long_term_memory.items
        if short_term_memory:
            yield sse_event(
                EVENT_SHORT_TERM_MEMORY_LOADED,
                {
                    "conversation_id": conversation_id,
                    "has_summary": bool(short_term_memory.get("summary")),
                    "has_state": bool(short_term_memory.get("state")),
                    "recent_message_count": len(
                        short_term_memory.get("recent_messages") or []
                    ),
                },
            )

        if long_term_memory is not None:
            yield sse_event(
                EVENT_LONG_TERM_MEMORY_RETRIEVAL_START,
                {
                    "query": long_term_memory.query,
                    "top_k": request.options.long_term_memory_top_k,
                    "latency_ms": long_term_memory.latency_ms,
                },
            )

            for memory in long_term_memory_items:
                yield sse_event(
                    EVENT_LONG_TERM_MEMORY_ITEM,
                    {
                        "memory_id": memory.item.id,
                        "memory_type": memory.item.memory_type,
                        "score": memory.score,
                        "content": memory.item.content,
                        "importance": memory.item.importance,
                        "confidence": memory.item.confidence,
                    },
                )

        try:
            params = {
                "conversation_id": conversation_id,
                "clean_message": clean_message,
                "selected_model": selected_model,
                "assistant_run_id": assistant_run_id,
                "request": request,
                "route_decision": route_decision,
                "route_ms": route_ms,
                "start": start,
                "short_term_memory": short_term_memory,
                "long_term_memory": long_term_memory,
                "long_term_memory_items": long_term_memory_items,
            }
            if route_decision.mode == "chat":
                yield from self._stream_chat(
                    **params,
                    provider=request.provider,
                )
                return
            if route_decision.mode == "agent":
                yield from self._stream_agent(
                    **params,
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
                    "latency": {
                        "route_ms": route_ms,
                        "agent_ms": None,
                        "total_ms": latency_ms,
                    },
                },
            )

            yield sse_event(
                EVENT_ERROR,
                {
                    "code": "ASSISTANT_STREAM_ERROR",
                    "message": "Assistant 处理失败",
                    "detail": str(exc),
                },
            )
            yield sse_event(EVENT_DONE, "[DONE]")

    def _stream_chat(
        self,
        *,
        conversation_id: str,
        clean_message: str,
        selected_model: str,
        provider: str | None,
        assistant_run_id: str,
        request: AssistantStreamRequest,
        route_decision: RouteDecision,
        route_ms: int,
        start: float,
        long_term_memory: LongTermMemoryRetrievalResult | None,
        long_term_memory_items: list[RetrievedLongTermMemory],
        short_term_memory: dict[str, Any] | None,
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
        llm_messages = context_builder.build_messages(
            conversation_id,
            conversation_state=(
                short_term_memory.get("state") if short_term_memory else None
            ),
            include_conversation_state=request.options.enable_short_term_memory,
            long_term_memory_items=long_term_memory_items,
        )

        llm_provider = get_llm_provider(provider)
        full_answer_parts: list[str] = []

        for chunk in llm_provider.stream_chat(
            message=llm_messages,
            model=selected_model,
        ):
            if chunk.done:
                break

            full_answer_parts.append(chunk.delta)
            yield sse_event(EVENT_DELTA, {"delta": chunk.delta})

        full_answer = "".join(full_answer_parts)
        latency_ms = int((perf_counter() - start) * 1000)

        conversation_state_write = None
        long_term_memory_write = None
        if request.options.update_conversation_state:
            conversation_state_write = self._write_conversation_state_from_turn(
                conversation_id=conversation_id,
                user_message=clean_message,
                assistant_answer=full_answer,
                previous_state=(
                    short_term_memory.get("state") if short_term_memory else None
                ),
                model=selected_model,
            )

        if (
            request.options.enable_long_term_memory
            and request.options.enable_long_term_memory_write
        ):
            long_term_memory_write = self.long_term_writer.write_from_turn(
                user_message=clean_message,
                assistant_answer=full_answer,
                conversation_id=conversation_id,
                source_message_id=user_message["id"],
                source_run_id=assistant_run_id,
                model=selected_model,
            )
            yield sse_event(
                EVENT_LONG_TERM_MEMORY_WRITE,
                long_term_memory_write.trace,
            )

        trace = {
            "route_decision": route_decision.model_dump(),
            "planner": {
                "type": None,
                "prompt_version": None,
                "fallback_count": 0,
                "decision_count": 0,
            },
            "agent_run_id": None,
            "tool_calls": [],
            "finish_reason": "chat_completed",
            "latency": {
                "route_ms": route_ms,
                "agent_ms": 0,
                "total_ms": latency_ms,
            },
            "context_message_count": len(llm_messages),
            "memory": {
                "short_term": self._build_short_term_memory_trace(
                    enabled=request.options.enable_short_term_memory,
                    short_term_memory=short_term_memory,
                    conversation_state_write=conversation_state_write,
                ),
                "working": self._build_working_memory_trace(
                    enabled=request.options.enable_working_memory,
                    working_memory=None,
                ),
                "long_term": self._build_long_term_memory_trace(
                    enabled=request.options.enable_long_term_memory,
                    long_term_memory=long_term_memory,
                    long_term_memory_write=long_term_memory_write,
                ),
            },
        }

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
                "trace": trace,
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
            EVENT_ASSISTANT_END,
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
        yield sse_event(EVENT_DONE, "[DONE]")

    def _route(
        self,
        *,
        conversation_id: str,
        request: AssistantStreamRequest,
        selected_model: str,
    ) -> RouteDecision:
        if request.mode != "auto":
            return RouteDecision(
                mode=request.mode,
                confidence=1.0,
                source="rule",
                reason="用户显式指定 Assistant 模式",
            )

        recent_messages = list_recent_messages(conversation_id, limit=6)
        context = RouterContext(
            conversation_id=conversation_id,
            message=request.message,
            recent_messages=recent_messages,
            options=request.options.model_dump(),
        )
        return self.mode_router.route(context, model=selected_model)

    def _stream_agent(
        self,
        *,
        conversation_id: str,
        clean_message: str,
        selected_model: str,
        assistant_run_id: str,
        request: AssistantStreamRequest,
        route_decision: RouteDecision,
        route_ms: int,
        start: float,
        short_term_memory: dict[str, Any] | None,
        long_term_memory: LongTermMemoryRetrievalResult | None,
        long_term_memory_items: list[RetrievedLongTermMemory],
    ) -> Iterable[str]:
        # 当前 AgentService.chat 是同步执行。
        agent_start = perf_counter()
        result = self.agent_service.chat(
            conversation_id=conversation_id,
            question=clean_message,
            top_k=request.options.top_k,
            score_threshold=request.options.score_threshold,
            max_steps=request.options.max_steps,
            model=selected_model,
            enable_working_memory=request.options.enable_working_memory,
            memory_context=(
                long_term_memory_items if request.options.enable_working_memory else []
            ),
            conversation_state=(
                short_term_memory.get("state")
                if request.options.enable_working_memory and short_term_memory
                else None
            ),
        )
        agent_ms = int((perf_counter() - agent_start) * 1000)

        tool_calls: list[dict[str, Any]] = result.get("tool_calls", [])
        trace: dict[str, Any] = result.get("trace", {})
        answer: str = result.get("answer", "")
        agent_run_id: str | None = result.get("run_id")
        user_message_id: str | None = result.get("user_message_id")
        assistant_message_id: str | None = result.get("assistant_message_id")

        conversation_state_write = None
        long_term_memory_write = None

        if request.options.update_conversation_state:
            conversation_state_write = self._write_conversation_state_from_turn(
                conversation_id=conversation_id,
                user_message=clean_message,
                assistant_answer=answer,
                previous_state=(
                    short_term_memory.get("state") if short_term_memory else None
                ),
                model=selected_model,
            )

        if (
            request.options.enable_long_term_memory
            and request.options.enable_long_term_memory_write
        ):
            long_term_memory_write = self.long_term_writer.write_from_turn(
                user_message=clean_message,
                assistant_answer=answer,
                conversation_id=conversation_id,
                source_message_id=user_message_id,
                source_run_id=assistant_run_id,
                model=selected_model,
            )
            yield sse_event(
                EVENT_LONG_TERM_MEMORY_WRITE,
                long_term_memory_write.trace,
            )

        working_memory = trace.get("working_memory")
        if request.options.enable_working_memory_trace and working_memory is not None:
            yield sse_event(
                EVENT_WORKING_MEMORY_UPDATED,
                working_memory,
            )

        for tool_call in tool_calls:
            yield sse_event(
                EVENT_TOOL_CALL_START,
                {
                    "tool_name": tool_call.get("tool_name"),
                    "arguments": tool_call.get("arguments") or {},
                    "reason": tool_call.get("reason"),
                    "step": tool_call.get("step"),
                },
            )
            yield sse_event(
                EVENT_TOOL_CALL_END,
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
        yield sse_event(EVENT_DELTA, {"delta": answer})

        latency_ms = int((perf_counter() - start) * 1000)

        # 从 tool_calls 中兼容性抽取 sources（第一版）
        sources: list[dict[str, Any]] = self._extract_sources_from_tool_calls(
            tool_calls
        )

        assistant_trace: dict[str, Any] = {
            "route_decision": route_decision.model_dump(),
            "planner": self._normalize_planner_trace(trace.get("planner")),
            "agent_run_id": agent_run_id,
            "tool_calls": self._summarize_tool_calls(tool_calls),
            "finish_reason": trace.get("finish_reason"),
            "latency": {
                "route_ms": route_ms,
                "agent_ms": agent_ms,
                "total_ms": latency_ms,
            },
            "memory": {
                "short_term": self._build_short_term_memory_trace(
                    enabled=request.options.enable_short_term_memory,
                    short_term_memory=short_term_memory,
                    conversation_state_write=conversation_state_write,
                ),
                "working": self._build_working_memory_trace(
                    enabled=request.options.enable_working_memory,
                    working_memory=(
                        working_memory
                        if request.options.enable_working_memory_trace
                        else None
                    ),
                ),
                "long_term": self._build_long_term_memory_trace(
                    enabled=request.options.enable_long_term_memory,
                    long_term_memory=long_term_memory,
                    long_term_memory_write=long_term_memory_write,
                ),
            },
        }

        self.run_store.update_run(
            assistant_run_id,
            status="completed",
            user_message_id=user_message_id,
            assistant_message_id=assistant_message_id,
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
            EVENT_ASSISTANT_END,
            {
                "assistant_run_id": assistant_run_id,
                "assistant_message_id": assistant_message_id,
                "agent_run_id": agent_run_id,
                "mode": "agent",
                "latency_ms": latency_ms,
                "model": trace.get("model") or selected_model,
                "provider": trace.get("provider"),
                "tool_calls": tool_calls,
                "sources": sources,
                "trace": assistant_trace,
            },
        )
        yield sse_event(EVENT_DONE, "[DONE]")

    def _write_conversation_state_from_turn(
        self,
        *,
        conversation_id: str,
        user_message: str,
        assistant_answer: str,
        previous_state: dict[str, Any] | None,
        model: str | None,
    ) -> dict[str, Any]:
        state_patch = self.conversation_state_extractor.extract(
            user_message=user_message,
            assistant_answer=assistant_answer,
            previous_state=previous_state,
            model=model,
        )

        conversation_state = self.short_term_store.upsert_state(
            conversation_id=conversation_id,
            patch=state_patch,
        )

        return conversation_state.model_dump(mode="json")

    def _build_short_term_memory_trace(
        self,
        *,
        enabled: bool,
        short_term_memory: dict[str, Any] | None,
        conversation_state_write: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "enabled": enabled,
            "loaded": short_term_memory.get("trace") if short_term_memory else None,
            "state": short_term_memory.get("state") if short_term_memory else None,
            "write": conversation_state_write,
        }

    def _build_working_memory_trace(
        self,
        *,
        enabled: bool,
        working_memory: dict[str, Any] | None,
    ) -> dict[str, Any]:
        return {
            "enabled": enabled,
            "trace_enabled": enabled and bool(working_memory),
            "state": working_memory,
        }

    def _build_long_term_memory_trace(
        self,
        *,
        enabled: bool,
        long_term_memory: LongTermMemoryRetrievalResult | None,
        long_term_memory_write: LongTermMemoryWriteResult | None,
    ) -> dict[str, Any]:
        return {
            "enabled": enabled,
            "retrieval": long_term_memory.trace if long_term_memory else None,
            "items": (
                [
                    {
                        "id": item.item.id,
                        "type": item.item.memory_type,
                        "score": item.score,
                        "content": item.item.content,
                        "importance": item.item.importance,
                        "confidence": item.item.confidence,
                    }
                    for item in long_term_memory.items
                ]
                if long_term_memory
                else []
            ),
            "write": long_term_memory_write.trace if long_term_memory_write else None,
        }

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

    def _extract_sources_from_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """从 Agent tool_calls 中兼容性抽取 sources，供前端展示与后续 Eval 使用。

        抽取原则：
        - 优先级：result.data.items / result.data.chunks / result.data.sources
        → result.items / result.chunks / result.sources → result.data
        - 字段缺失时跳过，不抛异常。
        - 同一 chunk_id 去重。
        - content_preview 截断至 160 字。
        """
        seen_chunk_ids: set[str] = set()
        sources: list[dict[str, Any]] = []

        for tool_call in tool_calls:
            result_raw = tool_call.get("result")
            if not isinstance(result_raw, dict):
                # tool_result 有时是 AgentStep 序列化后的结构
                result_raw = tool_call.get("tool_result")
            if not isinstance(result_raw, dict):
                continue

            # 尝试多个候选位置，按优先级依次查找 item 列表
            candidate_lists: list[Any] = []
            data = result_raw.get("data")
            if isinstance(data, dict):
                for key in ("items", "chunks", "sources"):
                    v = data.get(key)
                    if isinstance(v, list):
                        candidate_lists.append(v)
                        break  # 找到即止
            for key in ("items", "chunks", "sources"):
                v = result_raw.get(key)
                if isinstance(v, list):
                    candidate_lists.append(v)
                    break

            for item_list in candidate_lists:
                for item in item_list:
                    if not isinstance(item, dict):
                        continue

                    chunk_id: str | None = item.get("chunk_id") or item.get("id")
                    # 去重
                    if chunk_id and chunk_id in seen_chunk_ids:
                        continue
                    if chunk_id:
                        seen_chunk_ids.add(chunk_id)

                    # content_preview：截断至 160 字
                    content: str = (
                        item.get("content") or item.get("content_preview") or ""
                    )
                    preview: str = content[:160] if content else ""

                    source: dict[str, Any] = {
                        "chunk_id": chunk_id,
                        "document_id": item.get("document_id"),
                        "filename": item.get("filename"),
                        "heading": item.get("heading"),
                        "score": item.get("score")
                        or item.get("rrf_score")
                        or item.get("rerank_score"),
                        "distance": item.get("distance"),
                        "rerank_score": item.get("rerank_score"),
                        "rrf_score": item.get("rrf_score"),
                        "chunk_index": item.get("chunk_index"),
                        "content_preview": preview,
                    }
                    sources.append(source)

        return sources

    def _summarize_tool_calls(
        self,
        tool_calls: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [
            {
                "step": tool_call.get("step"),
                "tool_name": tool_call.get("tool_name"),
                "success": tool_call.get("success"),
                "latency_ms": tool_call.get("latency_ms"),
            }
            for tool_call in tool_calls
        ]

    def _normalize_planner_trace(self, planner: Any) -> dict[str, Any]:
        if not isinstance(planner, dict):
            return {
                "type": None,
                "prompt_version": None,
                "fallback_count": 0,
                "decision_count": 0,
            }

        return {
            "type": planner.get("type"),
            "prompt_version": planner.get("prompt_version"),
            "fallback_count": int(planner.get("fallback_count") or 0),
            "decision_count": int(planner.get("decision_count") or 0),
        }
