from __future__ import annotations

from typing import Any

from src.app.db import get_connection


class ObservabilityMetrics:
    """基础 LLMOps 指标统计。"""

    def summary(self) -> dict[str, Any]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) AS span_count,
                        COUNT(*) FILTER (WHERE status = 'error') AS error_count,
                        COUNT(*) FILTER (WHERE span_type = 'llm.call') AS llm_call_count,
                        COUNT(*) FILTER (WHERE span_type = 'tool.call') AS tool_call_count,
                        COUNT(*) FILTER (WHERE span_type = 'mcp.call') AS mcp_call_count,
                        AVG(latency_ms) AS avg_latency_ms,
                        MAX(latency_ms) AS max_latency_ms
                    FROM trace_spans
                    WHERE started_at >= NOW() - INTERVAL '7 days'
                    """)
                row = cur.fetchone()

        return dict(row or {})
