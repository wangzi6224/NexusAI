from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from src.app.services.observability.metrics import ObservabilityMetrics
from src.app.services.observability.trace_store import TraceStore

router = APIRouter(prefix="/traces", tags=["traces"])


@router.get("/{trace_id}")
def get_trace(trace_id: str) -> dict[str, Any]:
    store = TraceStore()
    spans = store.list_spans(trace_id)

    if not spans:
        raise HTTPException(
            status_code=404,
            detail=f"Trace 不存在: {trace_id}",
        )

    return {
        "trace_id": trace_id,
        "summary": store.summarize_trace(trace_id),
        "spans": [span.model_dump(mode="json") for span in spans],
    }


@router.get("/{trace_id}/summary")
def get_trace_summary(trace_id: str) -> dict[str, Any]:
    return TraceStore().summarize_trace(trace_id)


@router.get("/metrics/observability")
def get_observability_metrics() -> dict[str, Any]:
    return ObservabilityMetrics().summary()
