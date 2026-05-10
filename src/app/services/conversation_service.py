from collections.abc import Iterable
from json import dumps
from time import perf_counter
from typing import Any

from src.app.config import get_ollama_model
from src.app.conversation_store import (
    count_messages,
    create_conversation,
    create_message,
    get_conversation,
    list_conversations,
    list_messages,
    list_recent_messages,
    update_conversation,
)
from src.app.exceptions import ConversationError
from src.app.logger import get_logger
from src.app.services.llm.ollama_provider import OllamaProvider

logger = get_logger()

DEFAULT_SYSTEM_PROMPT = "你是一个专业、耐心、严谨的 AI 开发学习助手。请使用简体中文回答。"
DEFAULT_CONTEXT_MESSAGE_LIMIT = 10


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
) -> dict[str, Any]:
    if not title.strip():
        raise ConversationError(
            message="会话标题不能为空",
            status_code=400,
        )

    return create_conversation(
        title=title.strip(),
        model=model,
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


def build_llm_messages(
    conversation_id: str,
    limit: int = DEFAULT_CONTEXT_MESSAGE_LIMIT,
) -> list[dict[str, str]]:
    conversation = _ensure_conversation_exists(conversation_id)
    recent_messages = list_recent_messages(conversation_id, limit=limit)

    llm_messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": DEFAULT_SYSTEM_PROMPT,
        }
    ]

    if conversation.get("summary"):
        llm_messages.append(
            {
                "role": "system",
                "content": f"当前会话摘要：{conversation['summary']}",
            }
        )

    for message in recent_messages:
        role = message["role"]

        if role not in {"user", "assistant", "system", "tool"}:
            continue

        llm_messages.append(
            {
                "role": role,
                "content": message["content"],
            }
        )

    return llm_messages


def send_conversation_message(
    conversation_id: str,
    content: str,
    model: str | None = None,
) -> dict[str, Any]:
    conversation = _ensure_conversation_exists(conversation_id)

    if not content.strip():
        raise ConversationError(
            message="消息内容不能为空",
            status_code=400,
        )

    selected_model = model or conversation.get("model") or get_ollama_model()

    user_message = create_message(
        conversation_id=conversation_id,
        role="user",
        content=content.strip(),
        metadata={},
    )

    llm_messages = build_llm_messages(conversation_id)

    provider = OllamaProvider()

    start = perf_counter()
    llm_response = provider.chat(
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

    update_conversation(conversation_id, {})

    logger.info(
        "会话消息处理完成: conversation_id=%s latency_ms=%s",
        conversation_id,
        latency_ms,
    )

    return {
        "user_message": user_message,
        "assistant_message": assistant_message,
    }


def _sse_event(event: str, data: Any) -> str:
    if isinstance(data, str):
        payload = data
    else:
        payload = dumps(data, ensure_ascii=False)

    return f"event: {event}\ndata: {payload}\n\n"


def stream_conversation_message(
    conversation_id: str,
    content: str,
    model: str | None = None,
) -> Iterable[str]:
    conversation = _ensure_conversation_exists(conversation_id)

    if not content.strip():
        yield _sse_event(
            "error",
            {
                "code": "CONVERSATION_ERROR",
                "message": "消息内容不能为空",
            },
        )
        yield _sse_event("done", "[DONE]")
        return

    selected_model = model or conversation.get("model") or get_ollama_model()

    try:
        user_message = create_message(
            conversation_id=conversation_id,
            role="user",
            content=content.strip(),
            metadata={},
        )

        llm_messages = build_llm_messages(conversation_id)

        yield _sse_event(
            "message_start",
            {
                "conversation_id": conversation_id,
                "user_message_id": user_message["id"],
            },
        )

        provider = OllamaProvider()
        full_answer_parts: list[str] = []

        start = perf_counter()

        for chunk in provider.stream_chat(
            messages=llm_messages,
            model=selected_model,
        ):
            if chunk.done:
                break

            full_answer_parts.append(chunk.delta)

            yield _sse_event(
                "delta",
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
                "provider": "ollama",
                "latency_ms": latency_ms,
                "context_message_count": len(llm_messages),
                "is_stream": True,
            },
        )

        update_conversation(conversation_id, {})

        yield _sse_event(
            "message_end",
            {
                "assistant_message_id": assistant_message["id"],
                "content": full_answer,
                "latency_ms": latency_ms,
            },
        )
        yield _sse_event("done", "[DONE]")

    except Exception as exc:
        logger.exception(
            "流式会话消息失败: conversation_id=%s error=%s",
            conversation_id,
            exc,
        )

        yield _sse_event(
            "error",
            {
                "code": "STREAM_CONVERSATION_MESSAGE_ERROR",
                "message": "流式会话消息失败",
                "detail": str(exc),
            },
        )
        yield _sse_event("done", "[DONE]")