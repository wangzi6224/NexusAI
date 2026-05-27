from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.app.schemas.schemas import ChatRequest, ChatResponse
from src.app.services.chat_service import handle_chat, handle_chat_stream

router = APIRouter()


# 聊天接口（同步）：接收用户消息并返回模型的完整响应
@router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["聊天"],
    summary="同步聊天",
    description="接收一条用户消息，调用当前模型生成完整回复后一次性返回。",
)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return handle_chat(message=request.message, model=request.model)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"模型调用失败: {exc}") from exc


# 聊天接口（流式）：以 Server-Sent Events 流式返回增量模型输出
@router.post(
    "/chat/stream",
    tags=["聊天"],
    summary="流式聊天",
    description="接收一条用户消息，通过 Server-Sent Events 持续返回模型增量输出。",
)
def chat_stream(request: ChatRequest) -> StreamingResponse:
    return StreamingResponse(
        handle_chat_stream(
            message=request.message,
            model=request.model,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

