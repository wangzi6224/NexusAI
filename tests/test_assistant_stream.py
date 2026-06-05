"""Week 15 Assistant Stream 相关测试。

测试点：
1. sse_event 输出格式正确
2. AssistantOrchestrator._extract_sources_from_tool_calls 各种结构兼容性
3. AssistantOrchestrator._extract_sources_from_tool_calls 去重逻辑
4. AssistantOrchestrator._extract_sources_from_tool_calls content_preview 截断
5. AssistantOrchestrator._extract_sources_from_tool_calls 空输入返回空列表
"""

from __future__ import annotations

import json

from src.app.services.assistant.event import (
    EVENT_ASSISTANT_END,
    EVENT_DELTA,
    EVENT_DONE,
    sse_event,
)
from src.app.schemas.assistant import AssistantStreamRequest
import src.app.services.context_builder as context_builder_module
import src.app.services.assistant.orchestrator as orchestrator_module
from src.app.services.assistant.llm_route_prompt import build_route_messages
from src.app.services.assistant.mode_router import RouterContext, RuleBasedModeRouter
from src.app.services.assistant.orchestrator import AssistantOrchestrator
from src.app.services.context_builder import ContextBuilder
from src.app.services.memory.long_term_schemas import (
    LongTermMemoryItem,
    LongTermMemoryRetrievalResult,
    LongTermMemoryWriteResult,
    RetrievedLongTermMemory,
)
from src.app.services.memory.working_memory import WorkingMemory

# ─── sse_event 格式测试 ────────────────────────────────────────────────────


class TestSseEvent:
    def test_string_data(self) -> None:
        result = sse_event(EVENT_DONE, "[DONE]")
        assert result == "event: done\ndata: [DONE]\n\n"

    def test_dict_data(self) -> None:
        result = sse_event(EVENT_DELTA, {"delta": "hello"})
        assert result.startswith("event: delta\ndata: ")
        data = json.loads(result.split("data: ", 1)[1].strip())
        assert data["delta"] == "hello"

    def test_format_has_double_newline(self) -> None:
        result = sse_event(EVENT_ASSISTANT_END, {"assistant_message_id": "msg-1"})
        assert result.endswith("\n\n")


# ─── _extract_sources_from_tool_calls 测试 ───────────────────────────────


class TestExtractSources:
    def setup_method(self) -> None:
        # 不需要真实 DB，直接实例化（只调用私有方法）
        self.orchestrator = AssistantOrchestrator.__new__(AssistantOrchestrator)

    def test_empty_tool_calls(self) -> None:
        sources = self.orchestrator._extract_sources_from_tool_calls([])
        assert sources == []

    def test_no_result_field(self) -> None:
        sources = self.orchestrator._extract_sources_from_tool_calls(
            [{"tool_name": "search_docs"}]
        )
        assert sources == []

    def test_extracts_from_result_data_items(self) -> None:
        tool_calls = [
            {
                "tool_name": "search_docs",
                "result": {
                    "data": {
                        "items": [
                            {
                                "chunk_id": "c1",
                                "document_id": "d1",
                                "filename": "file.md",
                                "content": "hello world",
                                "score": 0.88,
                            }
                        ]
                    }
                },
            }
        ]
        sources = self.orchestrator._extract_sources_from_tool_calls(tool_calls)
        assert len(sources) == 1
        assert sources[0]["chunk_id"] == "c1"
        assert sources[0]["filename"] == "file.md"
        assert sources[0]["score"] == 0.88
        assert sources[0]["content_preview"] == "hello world"

    def test_extracts_from_result_chunks(self) -> None:
        tool_calls = [
            {
                "tool_name": "search_docs",
                "result": {
                    "chunks": [
                        {"chunk_id": "c2", "filename": "doc.txt", "content": "x" * 200}
                    ]
                },
            }
        ]
        sources = self.orchestrator._extract_sources_from_tool_calls(tool_calls)
        assert len(sources) == 1
        # content_preview 截断至 160 字
        assert len(sources[0]["content_preview"]) == 160

    def test_deduplication_by_chunk_id(self) -> None:
        item = {"chunk_id": "same-id", "filename": "f.md", "content": "abc"}
        tool_calls = [
            {"tool_name": "t1", "result": {"items": [item]}},
            {"tool_name": "t2", "result": {"items": [item]}},
        ]
        sources = self.orchestrator._extract_sources_from_tool_calls(tool_calls)
        # 同一 chunk_id 只保留第一次
        assert len(sources) == 1

    def test_no_exception_on_malformed_input(self) -> None:
        tool_calls = [
            {"tool_name": "t1", "result": "not a dict"},
            {"tool_name": "t2", "result": {"data": "not a dict"}},
            {"tool_name": "t3", "result": {"items": ["not a dict", 42]}},
        ]
        # 不应该抛异常
        sources = self.orchestrator._extract_sources_from_tool_calls(tool_calls)
        assert isinstance(sources, list)


class TestAssistantTraceHelpers:
    def setup_method(self) -> None:
        self.orchestrator = AssistantOrchestrator.__new__(AssistantOrchestrator)

    def test_summarizes_tool_calls_for_assistant_run_trace(self) -> None:
        tool_calls = [
            {
                "step": 1,
                "tool_name": "search_docs",
                "success": True,
                "latency_ms": 132,
                "result": {"data": {"items": [{"content": "ignored"}]}},
            }
        ]

        summary = self.orchestrator._summarize_tool_calls(tool_calls)

        assert summary == [
            {
                "step": 1,
                "tool_name": "search_docs",
                "success": True,
                "latency_ms": 132,
            }
        ]

    def test_normalizes_missing_planner_trace(self) -> None:
        planner = self.orchestrator._normalize_planner_trace(None)

        assert planner == {
            "type": None,
            "prompt_version": None,
            "fallback_count": 0,
            "decision_count": 0,
        }

    def test_writes_conversation_state_from_turn(self) -> None:
        class FakeExtractor:
            def __init__(self) -> None:
                self.calls = []

            def extract(self, **kwargs):
                self.calls.append(kwargs)
                return {"current_topic": "记忆"}

        class FakeState:
            def model_dump(self, mode: str):
                assert mode == "json"
                return {"current_topic": "记忆"}

        class FakeStore:
            def __init__(self) -> None:
                self.calls = []

            def upsert_state(self, **kwargs):
                self.calls.append(kwargs)
                return FakeState()

        extractor = FakeExtractor()
        store = FakeStore()
        self.orchestrator.conversation_state_extractor = extractor
        self.orchestrator.short_term_store = store

        result = self.orchestrator._write_conversation_state_from_turn(
            conversation_id="conv-1",
            user_message="你好",
            assistant_answer="你好，有什么可以帮你？",
            previous_state={"current_topic": "寒暄"},
            model="deepseek-chat",
        )

        assert result == {"current_topic": "记忆"}
        assert extractor.calls == [
            {
                "user_message": "你好",
                "assistant_answer": "你好，有什么可以帮你？",
                "previous_state": {"current_topic": "寒暄"},
                "model": "deepseek-chat",
            }
        ]
        assert store.calls == [
            {
                "conversation_id": "conv-1",
                "patch": {"current_topic": "记忆"},
            }
        ]

    def test_builds_three_layer_memory_trace(self) -> None:
        memory = RetrievedLongTermMemory(
            item=LongTermMemoryItem(
                id="mem-1",
                memory_type="project",
                content="用户偏好最小范围修改。",
                importance=0.8,
                confidence=0.9,
            ),
            score=0.72,
            rank=1,
        )
        retrieval = LongTermMemoryRetrievalResult(
            query="怎么改？",
            items=[memory],
            latency_ms=12,
            trace={"candidate_count": 1},
        )
        write_result = LongTermMemoryWriteResult(
            trace={"candidate_count": 1, "created_count": 1}
        )

        trace = {
            "short_term": self.orchestrator._build_short_term_memory_trace(
                enabled=True,
                short_term_memory={
                    "trace": {"has_state": True},
                    "state": {"conversation_id": "conv-1"},
                },
                conversation_state_write={"conversation_id": "conv-1"},
            ),
            "working": self.orchestrator._build_working_memory_trace(
                enabled=True,
                working_memory={"memory_context": [memory.model_dump(mode="json")]},
            ),
            "long_term": self.orchestrator._build_long_term_memory_trace(
                enabled=True,
                long_term_memory=retrieval,
                long_term_memory_write=write_result,
            ),
        }

        assert trace["short_term"]["loaded"]["has_state"] is True
        assert trace["working"]["state"]["memory_context"][0]["item"]["id"] == "mem-1"
        assert trace["long_term"]["items"][0]["id"] == "mem-1"
        assert trace["long_term"]["write"]["created_count"] == 1

    def test_stream_returns_sse_error_when_route_fails(self, monkeypatch) -> None:
        monkeypatch.setattr(
            orchestrator_module,
            "get_conversation",
            lambda conversation_id: {
                "id": conversation_id,
                "model": "deepseek-chat",
                "provider": "deepseek",
            },
        )
        monkeypatch.setattr(
            orchestrator_module,
            "resolve_llm_model",
            lambda **kwargs: "deepseek-chat",
        )

        class FakeRunStore:
            def create_run(self, **kwargs):
                raise AssertionError("create_run should not run after route failure")

        orchestrator = AssistantOrchestrator.__new__(AssistantOrchestrator)
        orchestrator.run_store = FakeRunStore()

        def raise_route_error(**kwargs):
            raise RuntimeError("route failed")

        orchestrator._route = raise_route_error

        events = list(
            orchestrator.stream(
                conversation_id="conv-1",
                request=AssistantStreamRequest(message="你好"),
            )
        )

        assert events[0].startswith("event: error\n")
        assert "ASSISTANT_ROUTE_ERROR" in events[0]
        assert events[-1] == "event: done\ndata: [DONE]\n\n"


class TestAssistantModeRouting:
    def test_knowledge_query_routes_to_agent(self) -> None:
        router = RuleBasedModeRouter()

        decision = router.route(
            RouterContext(
                conversation_id="conv-1",
                message="根据知识库回答这个问题",
                recent_messages=[],
                options={},
            )
        )

        assert decision is not None
        assert decision.mode == "agent"

    def test_llm_route_prompt_does_not_expose_rag_mode(self) -> None:
        messages = build_route_messages(
            message="我都有什么文档",
            recent_messages=[],
            options={},
        )

        system_prompt = messages[0]["content"]
        assert '"mode": "chat|agent|mcp"' in system_prompt
        assert '"mode": "chat|rag|agent|mcp"' not in system_prompt


class TestLongTermMemoryContext:
    def test_context_builder_formats_retrieved_long_term_memory(self) -> None:
        builder = ContextBuilder.__new__(ContextBuilder)
        memory = RetrievedLongTermMemory(
            item=LongTermMemoryItem(
                id="mem-1",
                memory_type="project",
                content="用户偏好最小范围修改。",
                importance=0.8,
                confidence=0.9,
            ),
            score=0.72,
            rank=1,
        )

        text = builder._format_long_term_memory([memory])

        assert text is not None
        assert "长期记忆检索结果" in text
        assert "project" in text
        assert "用户偏好最小范围修改。" in text

    def test_context_builder_can_skip_short_term_state(self, monkeypatch) -> None:
        monkeypatch.setattr(
            context_builder_module,
            "list_recent_messages",
            lambda conversation_id, limit: [],
        )
        builder = ContextBuilder.__new__(ContextBuilder)
        builder.max_recent_messages = 10
        builder.max_context_chars = 12000
        builder.system_prompt = "system"
        builder._ensure_conversation_exists = lambda conversation_id: {
            "id": conversation_id,
            "summary": None,
        }

        messages = builder.build_messages(
            "conv-1",
            conversation_state={
                "conversation_id": "conv-1",
                "current_topic": "短期记忆",
            },
            include_conversation_state=False,
        )

        assert all("当前会话结构化状态" not in item["content"] for item in messages)

    def test_working_memory_accepts_serialized_long_term_memory_context(self) -> None:
        memory = RetrievedLongTermMemory(
            item=LongTermMemoryItem(
                id="mem-1",
                memory_type="semantic",
                content="长期记忆会进入 Agent 工作记忆。",
            ),
            score=0.66,
            rank=1,
        )

        working_memory = WorkingMemory(
            memory_context=[memory.model_dump(mode="json")]
        )

        assert working_memory.memory_context[0]["item"]["id"] == "mem-1"
        assert working_memory.memory_context[0]["score"] == 0.66
