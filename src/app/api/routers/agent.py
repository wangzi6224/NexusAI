from functools import lru_cache
from typing import Any

from fastapi import APIRouter
from src.app.agent_trace_store import (
    get_agent_run,
    list_agent_events,
    list_agent_runs_by_conversation,
    list_agent_steps,
)
from src.app.schemas.agent import AgentRunDetailResponse
from src.app.schemas.agent import AgentChatRequest, AgentChatResponse
from src.app.services.agent.agent_service import AgentService
from src.app.exceptions import ConversationError

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


# 获取 Agent Run 详情，包括基本信息、步骤列表和事件列表
@router.get("/runs/{run_id}", response_model=AgentRunDetailResponse)
def get_agent_run_detail(run_id: str) -> AgentRunDetailResponse:
    run = get_agent_run(run_id)

    if run is None:
        raise ConversationError(
            message="Agent Run 不存在",
            detail=f"run_id={run_id}",
            status_code=404,
        )

    return AgentRunDetailResponse(
        run=run,
        steps=list_agent_steps(run_id),
        events=list_agent_events(run_id),
    )


# 获取指定会话的 Agent Run 列表
@router.get("/conversations/{conversation_id}/runs")
def list_conversation_agent_runs(conversation_id: str) -> dict[str, Any]:
    return {
        "conversation_id": conversation_id,
        "runs": list_agent_runs_by_conversation(conversation_id),
    }
