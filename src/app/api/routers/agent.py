from functools import lru_cache

from fastapi import APIRouter

from src.app.schemas.agent import AgentChatRequest, AgentChatResponse
from src.app.services.agent.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])


@lru_cache
def get_agent_service() -> AgentService:
    return AgentService()


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(
    request: AgentChatRequest,
) -> AgentChatResponse:
    result = get_agent_service().chat(
        conversation_id=request.conversation_id,
        question=request.question,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        max_steps=request.max_steps,
        model=request.model,
    )

    return AgentChatResponse(**result)
