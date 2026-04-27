from datetime import datetime
from time import perf_counter

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
