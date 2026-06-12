from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from src.app.services.observability.trace_schema import SpanType
from src.app.services.observability.trace_schema import TraceSpanCreate
from src.app.services.observability.trace_store import TraceStore


@contextmanager
def trace_span(
    *,
    trace_id: str,
    run_id: str,
    span_type: SpanType,
    name: str,
    parent_span_id: str | None = None,
    conversation_id: str | None = None,
    assistant_run_id: str | None = None,
    agent_run_id: str | None = None,
    input: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    store: TraceStore | None = None,
) -> Iterator[str]:
    """创建并自动结束一个 TraceSpan。"""

    trace_store = store or TraceStore()

    span = trace_store.create_span(
        TraceSpanCreate(
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            run_id=run_id,
            conversation_id=conversation_id,
            assistant_run_id=assistant_run_id,
            agent_run_id=agent_run_id,
            span_type=span_type,
            name=name,
            input=input or {},
            metadata=metadata or {},
        )
    )

    try:
        yield span.id
        trace_store.finish_span(span.id, status="success")
    except Exception as exc:
        trace_store.finish_span(
            span.id,
            status="error",
            error_code=exc.__class__.__name__,
            error_message=str(exc),
        )
        raise
