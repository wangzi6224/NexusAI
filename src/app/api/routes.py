from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from src.app.paths import STATIC_DIR
from src.app.schemas import ChatRequest, ChatResponse, HealthResponse
from src.app.services.chat_service import handle_chat
from src.app.services.health_service import get_health_status

router = APIRouter()


@router.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return get_health_status()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        return handle_chat(request.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"模型调用失败: {exc}") from exc
