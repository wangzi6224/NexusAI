from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from src.app.paths import STATIC_DIR
from src.app.schemas import (
    ChatRequest,
    ChatResponse,
    ClearHistoryResponse,
    HealthResponse,
    HistoryItem,
    ModelsResponse,
    SelectModelRequest,
    SelectModelResponse,
)
from src.app.services.model_service import get_models, select_model
from src.app.services.history_service import clear_chat_history, get_history
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
    
@router.get("/history", response_model=list[HistoryItem])
def get_chat_history() -> list[HistoryItem]:
    records = get_history()
    return [HistoryItem(**record) for record in records]


@router.post("/history/clear", response_model=ClearHistoryResponse)
def clear_history() -> ClearHistoryResponse:
    try:
        clear_chat_history()
        return ClearHistoryResponse(success=True, message="聊天记录已清空")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"清空聊天记录失败: {exc}") from exc

@router.get("/models", response_model=ModelsResponse)
def models() -> ModelsResponse:
    return get_models()


@router.post("/model/select", response_model=SelectModelResponse)
def select_model_api(request: SelectModelRequest) -> SelectModelResponse:
    try:
        return select_model(request.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
