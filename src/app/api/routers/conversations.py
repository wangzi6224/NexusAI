from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.app.schemas.schemas import (
    ContextPreviewResponse,
    ConversationCreateRequest,
    ConversationDetailResponse,
    ConversationItem,
    ConversationListResponse,
    MessageItem,
    MessageListResponse,
    SendMessageRequest,
    SendMessageResponse,
    SummaryUpdateResponse,
)
from src.app.services.conversation_service import (
    create_new_conversation,
    get_context_preview,
    get_conversation_detail,
    get_conversation_list,
    get_conversation_messages,
    send_conversation_message,
    stream_conversation_message,
    update_summary_manually,
)

router = APIRouter()


# 创建会话：新建一个会话并返回会话详情
@router.post(
    "/conversations",
    response_model=ConversationDetailResponse,
    tags=["会话"],
    summary="创建会话",
    description="创建一个新的多轮会话，可指定标题和模型。",
)
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
@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    tags=["会话"],
    summary="列出会话",
    description="返回所有多轮会话的摘要列表，用于会话侧边栏或列表页展示。",
)
def list_conversations_api() -> ConversationListResponse:
    conversations = get_conversation_list()
    return ConversationListResponse(
        items=[ConversationItem(**item) for item in conversations]
    )


# 获取会话详情：根据 conversation_id 返回会话完整信息
@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    tags=["会话"],
    summary="获取会话详情",
    description="根据会话 ID 返回单个会话的完整信息。",
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
    tags=["会话"],
    summary="列出会话消息",
    description="根据会话 ID 返回该会话下的全部消息列表。",
)
def list_conversation_messages_api(
    conversation_id: str,
) -> MessageListResponse:
    messages = get_conversation_messages(conversation_id)
    return MessageListResponse(items=[MessageItem(**item) for item in messages])


# 发送会话消息：向指定会话发送用户消息并返回用户/助手消息对象
@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=SendMessageResponse,
    tags=["会话"],
    summary="发送会话消息",
    description="向指定会话追加用户消息，并返回用户消息和助手回复消息。",
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
@router.post(
    "/conversations/{conversation_id}/messages/stream",
    tags=["会话"],
    summary="流式发送会话消息",
    description="向指定会话追加用户消息，并通过 Server-Sent Events 流式返回助手回复。",
)
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


# 预览会话上下文：查看实际发给模型前的上下文内容
@router.get(
    "/conversations/{conversation_id}/context-preview",
    response_model=ContextPreviewResponse,
    tags=["会话"],
    summary="预览会话上下文",
    description="查看指定会话组装给模型前的上下文内容，便于调试多轮上下文。",
)
def get_context_preview_api(
    conversation_id: str,
) -> ContextPreviewResponse:
    preview_data: dict[str, Any] = get_context_preview(conversation_id)
    return ContextPreviewResponse(**preview_data)


# 更新会话摘要：手动触发长会话摘要刷新
@router.post(
    "/conversations/{conversation_id}/summary",
    response_model=SummaryUpdateResponse,
    tags=["会话"],
    summary="更新会话摘要",
    description="手动触发指定会话的摘要更新，用于压缩和维护长对话上下文。",
)
def update_conversation_summary_api(
    conversation_id: str,
) -> SummaryUpdateResponse:
    result: dict[str, Any] = update_summary_manually(conversation_id)
    return SummaryUpdateResponse(**result)

