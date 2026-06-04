from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from src.app.services.memory.short_term_schemas import ConversationStatePatch
from src.app.services.memory.short_term_store import ShortTermMemoryStore
from src.app.services.memory.long_term_embedding import LongTermMemoryEmbeddingService
from src.app.services.memory.long_term_retriever import LongTermMemoryRetriever
from src.app.services.memory.long_term_schemas import (
    LongTermMemoryCreate,
    LongTermMemorySearchRequest,
    LongTermMemoryUpdate,
)
from src.app.services.memory.long_term_store import LongTermMemoryStore

router = APIRouter(prefix="/memories", tags=["memories"])


@router.get("/short-term/{conversation_id}")
def get_short_term_memory(conversation_id: str) -> dict[str, Any]:
    store = ShortTermMemoryStore()
    state = store.get_state(conversation_id)

    return {
        "conversation_id": conversation_id,
        "state": state.model_dump(mode="json") if state else None,
    }


@router.patch("/short-term/{conversation_id}")
def update_short_term_memory(
    conversation_id: str,
    payload: ConversationStatePatch,
) -> dict[str, Any]:
    store = ShortTermMemoryStore()
    state = store.upsert_state(conversation_id, payload)
    return state.model_dump(mode="json")


@router.get("/long-term")
def list_long_term_memories(
    user_id: str = "default_user",
    memory_type: str | None = None,
    status: str = "active",
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    store = LongTermMemoryStore()
    items = store.list(
        user_id=user_id,
        memory_type=memory_type,
        status=status,
        limit=limit,
        offset=offset,
    )

    return {
        "items": [item.model_dump(mode="json") for item in items],
        "limit": limit,
        "offset": offset,
    }


@router.post("/long-term")
def create_long_term_memory(payload: LongTermMemoryCreate) -> dict[str, Any]:
    store = LongTermMemoryStore()
    item = store.create(payload)
    return item.model_dump(mode="json")


@router.post("/long-term/search")
def search_long_term_memories(
    payload: LongTermMemorySearchRequest,
) -> dict[str, Any]:
    retriever = LongTermMemoryRetriever()
    result = retriever.retrieve(payload)
    return result.model_dump(mode="json")


@router.patch("/long-term/{memory_id}")
def update_long_term_memory(
    memory_id: str,
    payload: LongTermMemoryUpdate,
) -> dict[str, Any]:
    store = LongTermMemoryStore()

    try:
        item = store.update(memory_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return item.model_dump(mode="json")


@router.delete("/long-term/{memory_id}")
def delete_long_term_memory(memory_id: str) -> dict[str, Any]:
    store = LongTermMemoryStore()

    try:
        item = store.delete(memory_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return item.model_dump(mode="json")


@router.post("/long-term/embed-pending")
def embed_pending_long_term_memories(
    limit: int = Query(default=100, ge=1, le=500),
) -> dict[str, Any]:
    service = LongTermMemoryEmbeddingService()
    return service.embed_pending(limit=limit)
