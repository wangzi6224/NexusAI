from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from src.app.paths import STATIC_DIR
from src.app.schemas import (
    ChatRequest,
    HistoryItem,
    ChatResponse,
    HealthResponse,
    ModelsResponse,
    SelectModelRequest,
    SelectModelResponse,
    ClearHistoryResponse,
    ConversationCreateRequest,
    ConversationDetailResponse,
    ConversationItem,
    ConversationListResponse,
    MessageItem,
    MessageListResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from src.app.services.model_service import get_models, select_model
from src.app.services.history_service import clear_chat_history, get_history
from src.app.services.chat_service import handle_chat, handle_chat_stream
from src.app.services.health_service import get_health_status
from src.app.services.conversation_service import (
    create_new_conversation,
    get_conversation_detail,
    get_conversation_list,
    get_conversation_messages,
    send_conversation_message,
    stream_conversation_message
)

router = APIRouter()


# 首页路由：返回静态前端页面（index.html）
@router.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# 健康检查接口：返回服务状态信息
@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return get_health_status()


# 聊天接口（同步）：接收用户消息并返回模型的完整响应
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return handle_chat(message=request.message, model=request.model)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"模型调用失败: {exc}") from exc


# 聊天接口（流式）：以 Server-Sent Events 流式返回增量模型输出
@router.post("/chat/stream")
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


# 获取聊天记录：返回历史聊天条目列表
@router.get("/history", response_model=list[HistoryItem])
def get_chat_history() -> list[HistoryItem]:
    records = get_history()
    return [HistoryItem(**record) for record in records]


# 清空聊天记录：删除所有历史会话/消息
@router.post("/history/clear", response_model=ClearHistoryResponse)
def clear_history() -> ClearHistoryResponse:
    try:
        clear_chat_history()
        return ClearHistoryResponse(success=True, message="聊天记录已清空")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"清空聊天记录失败: {exc}") from exc

# 列出可用模型：返回当前支持的模型信息
@router.get("/models", response_model=ModelsResponse)
def models() -> ModelsResponse:
    return get_models()


# 选择模型接口：设置/切换使用的模型
@router.post("/model/select", response_model=SelectModelResponse)
def select_model_api(request: SelectModelRequest) -> SelectModelResponse:
    try:
        return select_model(request.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# 创建会话：新建一个会话并返回会话详情
@router.post("/conversations", response_model=ConversationDetailResponse)
def create_conversation_api(
    request: ConversationCreateRequest,
) -> ConversationDetailResponse:
    conversation = create_new_conversation(
        title=request.title,
        model=request.model,
    )
    return ConversationDetailResponse(
        **conversation,
        message_count=0,
    )


# 列出会话：返回所有会话的摘要列表
@router.get("/conversations", response_model=ConversationListResponse)
def list_conversations_api() -> ConversationListResponse:
    conversations = get_conversation_list()
    return ConversationListResponse(
        items=[ConversationItem(**item) for item in conversations]
    )


# 获取会话详情：根据 conversation_id 返回会话完整信息
@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation_api(
    conversation_id: str,
) -> ConversationDetailResponse:
    conversation = get_conversation_detail(conversation_id)
    return ConversationDetailResponse(**conversation)


# 列出会话消息：返回指定会话的消息列表
@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessageListResponse,
)
def list_conversation_messages_api(
    conversation_id: str,
) -> MessageListResponse:
    messages = get_conversation_messages(conversation_id)
    return MessageListResponse(
        items=[MessageItem(**item) for item in messages]
    )


# 发送会话消息：向指定会话发送用户消息并返回用户/助手消息对象
@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
)
def send_conversation_message_api(
    conversation_id: str,
    request: SendMessageRequest,
) -> SendMessageResponse:
    result = send_conversation_message(
        conversation_id=conversation_id,
        content=request.content,
        model=request.model,
    )

    return SendMessageResponse(
        user_message=MessageItem(**result["user_message"]),
        assistant_message=MessageItem(**result["assistant_message"]),
    )

# 发送会话消息，以 Server-Sent Events 流式返回增量模型输出
@router.post("/conversations/{conversation_id}/messages/stream")
def stream_conversation_message_api(
    conversation_id: str,
    request: SendMessageRequest,
) -> StreamingResponse:
    return StreamingResponse(
        stream_conversation_message(
            conversation_id=conversation_id,
            content=request.content,
            model=request.model,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
