from fastapi import APIRouter

from src.app.api.routers import (
    base,
    chat,
    conversations,
    documents,
    embeddings,
    history_models,
    rag,
)

router = APIRouter()

router.include_router(base.router)
router.include_router(chat.router)
router.include_router(history_models.router)
router.include_router(conversations.router)
router.include_router(documents.router)
router.include_router(embeddings.router)
router.include_router(rag.router)

__all__ = ["router"]
