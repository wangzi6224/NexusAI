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
from src.app.services.assistant.orchestrator import AssistantOrchestrator

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
