from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.app.schemas.assistant import AssistantStreamRequest
from src.app.services.assistant.orchestrator import AssistantOrchestrator

router = APIRouter(tags=["assistant"])


@lru_cache
def get_assistant_orchestrator() -> AssistantOrchestrator:
    return AssistantOrchestrator()


@router.post("/conversations/{conversation_id}/assistant/stream")
def stream_assistant_message(
    conversation_id: str,
    request: AssistantStreamRequest,
) -> StreamingResponse:
    return StreamingResponse(
        get_assistant_orchestrator().stream(
            conversation_id=conversation_id,
            request=request,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/assistant/runs/{run_id}")
def get_assistant_run(run_id: str) -> dict[str, Any]:
    """查询单条 AssistantRun 详情。"""
    return get_assistant_orchestrator().run_store.get_run(run_id)


@router.post("/conversations/{conversation_id}/assistant/context/debug")
def debug_assistant_context(
    conversation_id: str,
    request: AssistantStreamRequest,
) -> dict[str, Any]:
    return get_assistant_orchestrator().debug_context(
        conversation_id=conversation_id,
        request=request,
    )
