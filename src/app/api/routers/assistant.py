from __future__ import annotations

from functools import lru_cache

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
