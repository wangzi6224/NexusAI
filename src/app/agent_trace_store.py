from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from src.app.db import get_connection


def _normalize_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    """归一化数据库查询结果。

    Args:
        row: 查询返回的数据库行。

    Returns:
        若输入为 None 则返回 None；否则将 datetime 字段转换为 ISO 字符串，并保证 metadata 字段为字典。
    """
    if row is None:
        return None

    result = dict(row)

    for key in ["created_at", "updated_at"]:
        if isinstance(result.get(key), datetime):
            result[key] = result[key].isoformat()

    if result.get("metadata") is None:
        result["metadata"] = {}

    return result


def create_agent_run(
    *,
    conversation_id: str,
    user_message_id: str,
    input_text: str,
    model: str,
    provider: str = "ollama",
    max_steps: int = 3,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """创建新的 agent_runs 记录，并返回完整信息。

    Args:
        conversation_id: 该 Agent 运行所属的会话 ID。
        user_message_id: 触发该 Agent 运行的用户消息 ID。
        input_text: 用户输入的文本内容。
        model: Agent 执行使用的模型名称。
        provider: Agent 执行使用的模型提供商，默认为 "ollama"。
        max_steps: 该 Agent 运行允许的最大步骤数，默认为 3。
        metadata: 可选附加信息，将存储在 metadata 字段中。

    Returns:
        包含新创建的 agent_runs 记录完整信息的字典，datetime 字段已转换为 ISO 格式字符串。
    """

    run_id = str(uuid4())

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO agent_runs (
                    id,
                    conversation_id,
                    user_message_id,
                    status,
                    input,
                    model,
                    provider,
                    max_steps,
                    metadata
                )
                VALUES (
                    %(id)s,
                    %(conversation_id)s,
                    %(user_message_id)s,
                    'running',
                    %(input)s,
                    %(model)s,
                    %(provider)s,
                    %(max_steps)s,
                    %(metadata)s
                )
                RETURNING *
                """,
                {
                    "id": run_id,
                    "conversation_id": conversation_id,
                    "user_message_id": user_message_id,
                    "input": input_text,
                    "model": model,
                    "provider": provider,
                    "max_steps": max_steps,
                    "metadata": Jsonb(metadata or {}),
                },
            )
            row = cur.fetchone()
        conn.commit()

    return _normalize_row(row) or {}


def update_agent_run(
    run_id: str,
    *,
    status: str,
    final_answer: str | None = None,
    step_count: int | None = None,
    total_latency_ms: int | None = None,
    error_code: str | None = None,
    error_message: str | None = None,
) -> dict[str, Any] | None:
    """更新 agent_runs 记录的状态和执行结果。

    Args:
        run_id: 待更新的 agent run ID。
        status: 当前运行状态。
        final_answer: Agent 的最终回答。
        step_count: 已执行的步骤数。
        total_latency_ms: 总耗时，单位毫秒。
        error_code: 错误码。
        error_message: 错误描述。

    Returns:
        更新后的 agent_runs 记录，若记录不存在则返回 None。
    """
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE agent_runs
                SET
                    status = %(status)s,
                    final_answer = COALESCE(%(final_answer)s, final_answer),
                    step_count = COALESCE(%(step_count)s, step_count),
                    total_latency_ms = COALESCE(%(total_latency_ms)s, total_latency_ms),
                    error_code = %(error_code)s,
                    error_message = %(error_message)s,
                    updated_at = NOW()
                WHERE id = %(run_id)s
                RETURNING *
                """,
                {
                    "run_id": run_id,
                    "status": status,
                    "final_answer": final_answer,
                    "step_count": step_count,
                    "total_latency_ms": total_latency_ms,
                    "error_code": error_code,
                    "error_message": error_message,
                },
            )
            row = cur.fetchone()
        conn.commit()

    return _normalize_row(row)


def create_agent_step(
    *,
    run_id: str,
    step_index: int,
    step_type: str,
    reason: str | None = None,
    thought: str | None = None,
    tool_name: str | None = None,
    tool_arguments: dict[str, Any] | None = None,
    tool_result: dict[str, Any] | None = None,
    success: bool = True,
    latency_ms: int = 0,
    error_code: str | None = None,
    error_message: str | None = None,
) -> dict[str, Any]:
    """创建 agent_steps 记录，追踪 Agent 执行过程中的单步信息。

    Args:
        run_id: 所属 agent run ID。
        step_index: 步骤序号。
        step_type: 步骤类型。
        reason: 该步骤的原因。
        thought: Agent 的内部思路。
        tool_name: 调用的工具名称。
        tool_arguments: 工具参数。
        tool_result: 工具返回结果。
        success: 是否执行成功。
        latency_ms: 本步骤耗时，单位毫秒。
        error_code: 错误码。
        error_message: 错误描述。

    Returns:
        新创建的 agent_steps 记录。
    """
    step_id = str(uuid4())

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO agent_steps (
                    id,
                    run_id,
                    step_index,
                    step_type,
                    thought,
                    reason,
                    tool_name,
                    tool_arguments,
                    tool_result,
                    success,
                    latency_ms,
                    error_code,
                    error_message
                )
                VALUES (
                    %(id)s,
                    %(run_id)s,
                    %(step_index)s,
                    %(step_type)s,
                    %(thought)s,
                    %(reason)s,
                    %(tool_name)s,
                    %(tool_arguments)s,
                    %(tool_result)s,
                    %(success)s,
                    %(latency_ms)s,
                    %(error_code)s,
                    %(error_message)s
                )
                RETURNING *
                """,
                {
                    "id": step_id,
                    "run_id": run_id,
                    "step_index": step_index,
                    "step_type": step_type,
                    "thought": thought,
                    "reason": reason,
                    "tool_name": tool_name,
                    "tool_arguments": Jsonb(tool_arguments or {}),
                    "tool_result": (
                        Jsonb(tool_result) if tool_result is not None else None
                    ),
                    "success": success,
                    "latency_ms": latency_ms,
                    "error_code": error_code,
                    "error_message": error_message,
                },
            )
            row = cur.fetchone()
        conn.commit()

    return _normalize_row(row) or {}


def create_agent_event(
    *,
    run_id: str,
    event_type: str,
    payload: dict[str, Any] | None = None,
    step_id: str | None = None,
) -> dict[str, Any]:
    """创建 agent_events 记录，用于保存 Agent 运行过程中的事件数据。

    Args:
        run_id: 所属 agent run ID。
        event_type: 事件类型。
        payload: 事件负载内容。
        step_id: 关联的 agent_steps ID，可选。

    Returns:
        新创建的 agent_events 记录。
    """
    event_id = str(uuid4())

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO agent_events (
                    id,
                    run_id,
                    step_id,
                    event_type,
                    payload
                )
                VALUES (
                    %(id)s,
                    %(run_id)s,
                    %(step_id)s,
                    %(event_type)s,
                    %(payload)s
                )
                RETURNING *
                """,
                {
                    "id": event_id,
                    "run_id": run_id,
                    "step_id": step_id,
                    "event_type": event_type,
                    "payload": Jsonb(payload or {}),
                },
            )
            row = cur.fetchone()
        conn.commit()

    return _normalize_row(row) or {}


def get_agent_run(run_id: str) -> dict[str, Any] | None:
    """查询单个 agent_runs 记录。

    Args:
        run_id: 目标 agent run ID。

    Returns:
        对应的 agent_runs 记录，若不存在则返回 None。
    """
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM agent_runs WHERE id = %(run_id)s",
                {"run_id": run_id},
            )
            row = cur.fetchone()

    return _normalize_row(row)


def list_agent_steps(run_id: str) -> list[dict[str, Any]]:
    """列出指定 run_id 的所有 agent_steps，并按 step_index 升序排序。

    Args:
        run_id: 目标 agent run ID。

    Returns:
        按顺序排列的 agent_steps 记录列表。
    """
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT *
                FROM agent_steps
                WHERE run_id = %(run_id)s
                ORDER BY step_index ASC
                """,
                {"run_id": run_id},
            )
            rows = cur.fetchall()

    return [_normalize_row(row) or {} for row in rows]


def list_agent_events(run_id: str) -> list[dict[str, Any]]:
    """列出指定 run_id 的所有 agent_events，并按创建时间升序排序。

    Args:
        run_id: 目标 agent run ID。

    Returns:
        按创建时间升序排列的 agent_events 记录列表。
    """
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT *
                FROM agent_events
                WHERE run_id = %(run_id)s
                ORDER BY created_at ASC
                """,
                {"run_id": run_id},
            )
            rows = cur.fetchall()

    return [_normalize_row(row) or {} for row in rows]


def list_agent_runs_by_conversation(conversation_id: str) -> list[dict[str, Any]]:
    """查询指定 conversation_id 下的所有 agent_runs 记录。

    Args:
        conversation_id: 会话 ID。

    Returns:
        该会话下按创建时间降序排列的 agent_runs 记录列表。
    """
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                SELECT *
                FROM agent_runs
                WHERE conversation_id = %(conversation_id)s
                ORDER BY created_at DESC
                """,
                {"conversation_id": conversation_id},
            )
            rows = cur.fetchall()

    return [_normalize_row(row) or {} for row in rows]
