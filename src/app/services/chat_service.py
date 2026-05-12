from datetime import datetime
from time import perf_counter
from typing import Iterable
from json import dumps

from src.app.config import get_ollama_model
from src.app.history import append_history
from src.app.logger import get_logger
from src.app.prompts import build_chat_prompt
from src.app.schemas import ChatResponse, TokenUsage
from src.app.services.llm.ollama_provider import OllamaProvider

logger = get_logger()


def handle_chat(message: str, model: str | None = None) -> ChatResponse:
    selected_model = model or get_ollama_model()
    logger.info("收到聊天请求，provider=ollama, model=%s", selected_model)

    prompt = build_chat_prompt(message)

    messages = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    provider = OllamaProvider()

    start = perf_counter()
    llm_response = provider.chat(messages=messages, model=selected_model)
    elapsed = perf_counter() - start
    latency_ms = int(elapsed * 1000)

    append_history(
        {
            "timestamp": datetime.now().isoformat(),
            "model": llm_response.model,
            "user_input": message,
            "prompt": prompt,
            "answer": llm_response.content,
            "elapsed_seconds": round(elapsed, 2),
        }
    )

    logger.info("聊天请求处理完成，耗时 %s ms", latency_ms)

    return ChatResponse(
        answer=llm_response.content,
        provider=llm_response.provider,
        model=llm_response.model,
        latency_ms=latency_ms,
        usage=TokenUsage(
            prompt_tokens=llm_response.usage.prompt_tokens,
            completion_tokens=llm_response.usage.completion_tokens,
            total_tokens=llm_response.usage.total_tokens,
        ),
    )


def handle_chat_stream(message: str, model: str | None = None) -> Iterable[str]:
    selected_model = model or get_ollama_model()
    logger.info("收到聊天请求，provider=ollama, model=%s", selected_model)

    prompt = build_chat_prompt(message)

    msg = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    # 注意这里实例化 OllamaProvider 后续会改为工厂模式，根据配置选择不同的 LLMProvider 实现
    provider = OllamaProvider()

    # 用于拼接完整回答的列表
    full_answer_parts: list[str] = []

    # 记录开始时间
    start = perf_counter()

    try:
        for chunk in provider.stream_chat(message=msg, model=selected_model):

            # 如果当前 chunk 表示流结束（done=True），则跳出循环
            if chunk.done:
                break

            # 将增量内容添加到完整回答的列表中
            full_answer_parts.append(chunk.delta)

            # 构建 SSE 格式的消息并发送给前端
            payload = {
                "delta": chunk.delta,
                "done": False,
            }

            # 注意这里我们将 payload 转换为 JSON 字符串，并按照 SSE 的格式发送（以 "data: " 开头，末尾加上两个换行符）
            yield f"data: {dumps(payload, ensure_ascii=False)}\n\n"

        elapsed = perf_counter() - start
        latency_ms = int(elapsed * 1000)

        payload = {
            "delta": "",
            "done": True,
            "model": selected_model,
            "latency_ms": latency_ms,
        }

        # 将完整回答拼接成一个字符串
        full_answer = "".join(full_answer_parts)
        append_history(
            {
                "timestamp": datetime.now().isoformat(),
                "model": selected_model,
                "user_input": message,
                "prompt": prompt,
                "answer": full_answer,
                "elapsed_seconds": round(elapsed, 2),
            }
        )
        yield f"data: {dumps(payload, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        logger.info(
            f"聊天请求处理完成，完整回答长度 {len(full_answer)} 字符, 耗时 {latency_ms} ms"
        )
    except Exception as exc:
        logger.exception("流式聊天请求失败: %s", exc)

        error_payload = {
            "error": {
                "code": "STREAM_CHAT_ERROR",
                "message": "流式聊天失败",
                "detail": str(exc),
            }
        }

        yield f"data: {dumps(error_payload, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
