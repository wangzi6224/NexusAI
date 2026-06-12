"""API route modules grouped by product area."""

from src.app.api.routers import (
    agent,
    assistant,
    base,
    chat,
    conversations,
    documents,
    embeddings,
    history_models,
    rag,
    memory,
    mcp,
    traces,
)

ROUTERS = (
    base.router,
    assistant.router,
    chat.router,
    history_models.router,
    conversations.router,
    documents.router,
    embeddings.router,
    rag.router,
    agent.router,
    memory.router,
    mcp.router,
    traces.router,
)

__all__ = [
    "ROUTERS",
    "agent",
    "assistant",
    "base",
    "chat",
    "conversations",
    "documents",
    "embeddings",
    "history_models",
    "rag",
    "memory",
    "mcp",
    "traces",
]
