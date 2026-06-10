from __future__ import annotations

from typing import Any
from uuid import uuid4

from psycopg.types.json import Jsonb

from src.app.db import get_connection
from src.app.services.mcp.schemas import McpToolCallResult


class McpAuditStore:
    def create_log(
        self,
        *,
        result: McpToolCallResult,
        arguments: dict[str, Any],
        conversation_id: str | None = None,
        assistant_run_id: str | None = None,
        agent_run_id: str | None = None,
        risk_level: str = "low",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        log_id = f"mcp_audit_{uuid4().hex}"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO mcp_tool_audit_logs (
                        id,
                        assistant_run_id,
                        agent_run_id,
                        conversation_id,
                        server_name,
                        tool_name,
                        full_tool_name,
                        arguments,
                        success,
                        error_code,
                        error_message,
                        latency_ms,
                        result_chars,
                        risk_level,
                        metadata
                    ) VALUES (
                        %(id)s,
                        %(assistant_run_id)s,
                        %(agent_run_id)s,
                        %(conversation_id)s,
                        %(server_name)s,
                        %(tool_name)s,
                        %(full_tool_name)s,
                        %(arguments)s::jsonb,
                        %(success)s,
                        %(error_code)s,
                        %(error_message)s,
                        %(latency_ms)s,
                        %(result_chars)s,
                        %(risk_level)s,
                        %(metadata)s::jsonb
                    )
                    RETURNING *
                    """,
                    {
                        "id": log_id,
                        "assistant_run_id": assistant_run_id,
                        "agent_run_id": agent_run_id,
                        "conversation_id": conversation_id,
                        "server_name": result.server_name,
                        "tool_name": result.tool_name,
                        "full_tool_name": result.full_name,
                        "arguments": Jsonb(arguments),
                        "success": result.success,
                        "error_code": result.error_code,
                        "error_message": result.error_message,
                        "latency_ms": result.latency_ms,
                        "result_chars": len(result.content or ""),
                        "risk_level": risk_level,
                        "metadata": Jsonb(metadata or {}),
                    },
                )
                row = cur.fetchone()
                conn.commit()
                return dict(row)
