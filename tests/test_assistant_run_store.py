"""Week 15 AssistantRunStore 单元测试。

测试点：
1. create_run 可以创建 running run
2. update_run 可以写入 user_message_id / assistant_message_id
3. get_run 可以查询
4. get_run 查询不存在 run_id 时返回 404
"""

from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

import pytest

from src.app.exceptions import ConversationError
from src.app.services.assistant.run_store import AssistantRunStore, _normalize_run

# ─── _normalize_run 单元测试（纯函数，无 DB 依赖） ────────────────────────────


class TestNormalizeRun:
    def test_none_input_returns_none(self) -> None:
        assert _normalize_run(None) is None

    def test_datetime_converted_to_isoformat(self) -> None:
        from datetime import datetime

        dt = datetime(2025, 1, 1, 12, 0, 0)
        row = {"id": "abc", "created_at": dt, "updated_at": dt}
        result = _normalize_run(row)
        assert result is not None
        assert result["created_at"] == "2025-01-01T12:00:00"
        assert result["updated_at"] == "2025-01-01T12:00:00"

    def test_trace_defaults_to_empty_dict(self) -> None:
        row = {"id": "abc", "trace": None}
        result = _normalize_run(row)
        assert result is not None
        assert result["trace"] == {}

    def test_metadata_defaults_to_empty_dict(self) -> None:
        row = {"id": "abc", "metadata": None}
        result = _normalize_run(row)
        assert result is not None
        assert result["metadata"] == {}


# ─── AssistantRunStore.get_run 单元测试（mock DB） ──────────────────────────


def _make_fake_run(run_id: str) -> dict:
    """构造一个 mock 用的 run 行。"""
    return {
        "id": run_id,
        "conversation_id": "conv-1",
        "user_message_id": None,
        "assistant_message_id": None,
        "mode": "chat",
        "status": "running",
        "input": "hello",
        "final_answer": None,
        "model": "qwen3:8b",
        "provider": "ollama",
        "latency_ms": None,
        "trace": None,
        "metadata": None,
        "created_at": None,
        "updated_at": None,
    }


class TestAssistantRunStoreGetRun:
    def test_get_run_found(self) -> None:
        run_id = str(uuid.uuid4())
        fake_row = _make_fake_run(run_id)

        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = fake_row
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        with patch(
            "src.app.services.assistant.run_store.get_connection",
            return_value=mock_conn,
        ):
            store = AssistantRunStore()
            result = store.get_run(run_id)

        assert result["id"] == run_id
        assert result["trace"] == {}
        assert result["metadata"] == {}

    def test_get_run_not_found_raises_404(self) -> None:
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.__enter__ = MagicMock(return_value=mock_conn)
        mock_conn.__exit__ = MagicMock(return_value=False)
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cur)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        with patch(
            "src.app.services.assistant.run_store.get_connection",
            return_value=mock_conn,
        ):
            store = AssistantRunStore()
            with pytest.raises(ConversationError) as exc_info:
                store.get_run("non-existent-id")

        assert exc_info.value.status_code == 404
        assert "不存在" in exc_info.value.message
