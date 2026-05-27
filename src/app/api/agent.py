"""Compatibility import for the Agent API router.

New route modules should live under ``src.app.api.routers`` so the application
has one route aggregation path.
"""

from src.app.api.routers.agent import agent_chat, get_agent_service, router

__all__ = ["agent_chat", "get_agent_service", "router"]
