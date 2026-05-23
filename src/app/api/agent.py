# src/app/api/agent.py
from fastapi import APIRouter

from src.app.schemas.agent import AgentChatRequest, AgentChatResponse
from src.app.services.agent.agent_service import AgentService

router = APIRouter(prefix="/agent", tags=["agent"])

agent_service = AgentService()


@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(
    conversation_id: str,
    request: AgentChatRequest,
) -> AgentChatResponse:
    result = agent_service.chat(
        conversation_id=conversation_id,
        question=request.question,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        max_steps=request.max_steps,
        model=request.model,
    )

    return AgentChatResponse(**result)
