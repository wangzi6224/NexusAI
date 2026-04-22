from datetime import datetime
from time import perf_counter

from src.app.client import chat_completion
from src.app.config import get_ollama_model
from src.app.history import append_history
from src.app.logger import get_logger
from src.app.prompts import build_chat_prompt
from src.app.schemas import ChatResponse

logger = get_logger()


def handle_chat(message: str) -> ChatResponse:
    logger.info("收到聊天请求，model=%s", get_ollama_model())

    prompt = build_chat_prompt(message)

    start = perf_counter()
    answer = chat_completion(prompt)
    elapsed = perf_counter() - start

    append_history(
        {
            "timestamp": datetime.now().isoformat(),
            "model": get_ollama_model(),
            "user_input": message,
            "prompt": prompt,
            "answer": answer,
            "elapsed_seconds": round(elapsed, 2),
        }
    )

    logger.info("聊天请求处理完成，耗时 %.2f 秒", elapsed)

    return ChatResponse(
        answer=answer,
        model=get_ollama_model(),
        elapsed_seconds=round(elapsed, 2),
    )
