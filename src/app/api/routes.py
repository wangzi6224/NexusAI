from time import perf_counter
from datetime import datetime

from fastapi import APIRouter, HTTPException

from src.app.client import chat_completion
from src.app.config import get_ollama_model
from src.app.health import check_ollama_model_exists, check_ollama_server
from src.app.history import append_history
from src.app.logger import get_logger
from src.app.prompts import build_chat_prompt
from src.app.schemas import ChatRequest, ChatResponse, HealthResponse
from fastapi.responses import FileResponse

router = APIRouter()
logger = get_logger()

@router.get("/")
def index() -> FileResponse:
    return FileResponse("src/app/static/index.html")


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    ok, message = check_ollama_server()
    if not ok:
        return HealthResponse(ok=False, message=message)

    ok, message = check_ollama_model_exists()
    if not ok:
        return HealthResponse(ok=False, message=message)

    return HealthResponse(ok=True, message="服务和模型均正常")


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    logger.info("收到聊天请求，model=%s", get_ollama_model())

    prompt = build_chat_prompt(request.message)

    start = perf_counter()
    try:
        answer = chat_completion(prompt)
    except Exception as exc:
        logger.exception("调用模型失败: %s", exc)
        raise HTTPException(status_code=500, detail=f"模型调用失败: {exc}") from exc

    elapsed = perf_counter() - start

    append_history(
        {
            "timestamp": datetime.now().isoformat(),
            "model": get_ollama_model(),
            "user_input": request.message,
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

