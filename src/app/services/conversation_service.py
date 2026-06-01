from collections.abc import Iterable
from json import dumps
from time import perf_counter
from typing import Any

from src.app.services.context_builder import ContextBuilder
from src.app.services.summarizer import Summarizer
from src.app.config import resolve_llm_model
from src.app.conversation_store import (
    count_messages,
    create_conversation,
    create_message,
    delete_conversation as store_delete_conversation,
    get_conversation,
    list_conversations,
    list_messages,
    update_conversation,
)
from src.app.exceptions import ConversationError
from src.app.logger import get_logger
from src.app.services.assistant.event import (
    ConversationStreamEvent,
    EVENT_DELTA,
    EVENT_DONE,
    EVENT_ERROR,
    EVENT_MESSAGE_END,
    EVENT_MESSAGE_START,
)
from src.app.services.llm.factory import get_llm_provider

logger = get_logger()


def _ensure_conversation_exists(conversation_id: str) -> dict[str, Any]:
    conversation = get_conversation(conversation_id)

    if conversation is None:
        raise ConversationError(
            message="会话不存在",
            detail=f"conversation_id={conversation_id}",
            status_code=404,
        )

    return conversation


def _with_message_count(conversation: dict[str, Any]) -> dict[str, Any]:
    return {
        **conversation,
        "message_count": count_messages(conversation["id"]),
    }


def create_new_conversation(
    title: str,
    model: str | None = None,
    provider: str | None = None,
) -> dict[str, Any]:
    if not title.strip():
        raise ConversationError(
            message="会话标题不能为空",
            status_code=400,
        )

    return create_conversation(
        title=title.strip(),
        model=model,
        provider=provider,
    )


def get_conversation_list() -> list[dict[str, Any]]:
    conversations = list_conversations()
    return [_with_message_count(item) for item in conversations]


def get_conversation_detail(conversation_id: str) -> dict[str, Any]:
    conversation = _ensure_conversation_exists(conversation_id)
    return _with_message_count(conversation)


def get_conversation_messages(conversation_id: str) -> list[dict[str, Any]]:
    _ensure_conversation_exists(conversation_id)
    return list_messages(conversation_id)


def send_conversation_message(
    conversation_id: str,
    content: str,
    model: str | None = None,
    provider: str | None = None,
) -> dict[str, Any]:
    conversation = _ensure_conversation_exists(conversation_id)

    if not content.strip():
        raise ConversationError(
            message="消息内容不能为空",
            status_code=400,
        )

    selected_model = resolve_llm_model(
        model=model,
        stored_model=conversation.get("model"),
        stored_provider=conversation.get("provider"),
        provider=provider,
    )

    user_message = create_message(
        conversation_id=conversation_id,
        role="user",
        content=content.strip(),
        metadata={},
    )
    context_builder = ContextBuilder()
    llm_messages = context_builder.build_messages(conversation_id)

    llm_provider = get_llm_provider(provider)

    start = perf_counter()
    llm_response = llm_provider.chat(
        messages=llm_messages,
        model=selected_model,
    )
    elapsed = perf_counter() - start
    latency_ms = int(elapsed * 1000)

    assistant_message = create_message(
        conversation_id=conversation_id,
        role="assistant",
        content=llm_response.content,
        metadata={
            "model": llm_response.model,
            "provider": llm_response.provider,
            "latency_ms": latency_ms,
            "context_message_count": len(llm_messages),
            "is_stream": False,
        },
    )

    _try_update_summary(conversation_id, model=selected_model)

    update_conversation(
        conversation_id,
        {
            "model": llm_response.model,
            "provider": llm_response.provider,
        },
    )

    logger.info(
        "会话消息处理完成: conversation_id=%s latency_ms=%s",
        conversation_id,
        latency_ms,
    )

    return {
        "user_message": user_message,
        "assistant_message": assistant_message,
    }


def _sse_event(event: ConversationStreamEvent, data: Any) -> str:
    if isinstance(data, str):
        payload = data
    else:
        payload = dumps(data, ensure_ascii=False)

    return f"event: {event}\ndata: {payload}\n\n"


def stream_conversation_message(
    conversation_id: str,
    content: str,
    model: str | None = None,
    provider: str | None = None,
) -> Iterable[str]:
    conversation = _ensure_conversation_exists(conversation_id)

    if not content.strip():
        yield _sse_event(
            EVENT_ERROR,
            {
                "code": "CONVERSATION_ERROR",
                "message": "消息内容不能为空",
            },
        )
        yield _sse_event(EVENT_DONE, "[DONE]")
        return

    selected_model = resolve_llm_model(
        model=model,
        stored_model=conversation.get("model"),
        stored_provider=conversation.get("provider"),
        provider=provider,
    )

    try:
        user_message = create_message(
            conversation_id=conversation_id,
            role="user",
            content=content.strip(),
            metadata={},
        )

        context_builder = ContextBuilder()
        llm_messages = context_builder.build_messages(conversation_id)

        yield _sse_event(
            EVENT_MESSAGE_START,
            {
                "conversation_id": conversation_id,
                "user_message_id": user_message["id"],
            },
        )

        llm_provider = get_llm_provider(provider)
        full_answer_parts: list[str] = []

        start = perf_counter()

        for chunk in llm_provider.stream_chat(
            message=llm_messages,
            model=selected_model,
        ):
            if chunk.done:
                break

            full_answer_parts.append(chunk.delta)

            yield _sse_event(
                EVENT_DELTA,
                {
                    "delta": chunk.delta,
                },
            )

        elapsed = perf_counter() - start
        latency_ms = int(elapsed * 1000)
        full_answer = "".join(full_answer_parts)

        assistant_message = create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_answer,
            metadata={
                "model": selected_model,
                "provider": llm_provider.name,
                "latency_ms": latency_ms,
                "context_message_count": len(llm_messages),
                "is_stream": True,
            },
        )

        _try_update_summary(conversation_id, model=selected_model)

        update_conversation(
            conversation_id,
            {
                "model": selected_model,
                "provider": llm_provider.name,
            },
        )

        yield _sse_event(
            EVENT_MESSAGE_END,
            {
                "assistant_message_id": assistant_message["id"],
                "content": full_answer,
                "latency_ms": latency_ms,
            },
        )
        yield _sse_event(EVENT_DONE, "[DONE]")

    except Exception as exc:
        logger.exception(
            "流式会话消息失败: conversation_id=%s error=%s",
            conversation_id,
            exc,
        )

        yield _sse_event(
            EVENT_ERROR,
            {
                "code": "STREAM_CONVERSATION_MESSAGE_ERROR",
                "message": "流式会话消息失败",
                "detail": str(exc),
            },
        )
        yield _sse_event(EVENT_DONE, "[DONE]")


def update_summary_manually(conversation_id: str) -> dict[str, Any]:
    summarizer = Summarizer()
    return summarizer.summarize(conversation_id)


def _try_update_summary(
    conversation_id: str,
    model: str | None = None,
) -> None:
    summarizer = Summarizer()

    try:
        if not summarizer.should_update(conversation_id):
            return

        start_time: float = perf_counter()  # 预热 perf_counter，减少首次调用的误差

        logger.info(
            "开始更新会话摘要: conversation_id=%s",
            conversation_id,
        )

        summarizer.summarize(
            conversation_id=conversation_id,
            model=model,
        )

        end_time = perf_counter()
        elapsed_ms = int((end_time - start_time) * 1000)

        logger.info(
            "会话摘要已更新: conversation_id=%s, elapsed_ms=%s",
            conversation_id,
            elapsed_ms,
        )

    except Exception as exc:
        logger.exception(
            "自动更新会话摘要失败: conversation_id=%s error=%s",
            conversation_id,
            exc,
        )


def delete_conversation_by_id(conversation_id: str) -> dict[str, Any]:
    _ensure_conversation_exists(conversation_id)

    deleted = store_delete_conversation(conversation_id)

    if not deleted:
        raise ConversationError(
            message="删除会话失败",
            detail=f"conversation_id={conversation_id}",
            status_code=500,
        )

    logger.info("会话已删除: conversation_id=%s", conversation_id)

    return {
        "success": True,
        "message": "会话已删除",
        "conversation_id": conversation_id,
    }


def get_context_preview(conversation_id: str) -> dict[str, Any]:
    context_data = ContextBuilder().build_preview(conversation_id)
    return context_data
