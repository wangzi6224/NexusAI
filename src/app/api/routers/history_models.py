from fastapi import APIRouter, HTTPException

from src.app.schemas.schemas import (
    ClearHistoryResponse,
    HistoryItem,
    ModelsResponse,
    SelectModelRequest,
    SelectModelResponse,
)
from src.app.services.history_service import clear_chat_history, get_history
from src.app.services.model_service import get_models, select_model

router = APIRouter()


# 获取聊天记录：返回历史聊天条目列表
@router.get(
    "/history",
    response_model=list[HistoryItem],
    tags=["历史与模型"],
    summary="获取聊天记录",
    description="读取并返回普通聊天接口保存的历史消息列表。",
)
def get_chat_history() -> list[HistoryItem]:
    records = get_history()
    return [HistoryItem(**record) for record in records]


# 清空聊天记录：删除所有历史会话/消息
@router.post(
    "/history/clear",
    response_model=ClearHistoryResponse,
    tags=["历史与模型"],
    summary="清空聊天记录",
    description="删除普通聊天接口保存的全部历史消息。",
)
def clear_history() -> ClearHistoryResponse:
    try:
        clear_chat_history()
        return ClearHistoryResponse(success=True, message="聊天记录已清空")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"清空聊天记录失败: {exc}") from exc


# 列出可用模型：返回当前支持的模型信息
@router.get(
    "/models",
    response_model=ModelsResponse,
    tags=["历史与模型"],
    summary="列出可用模型",
    description="返回当前后端可用的模型列表，以及当前选中的模型信息。",
)
def models() -> ModelsResponse:
    return get_models()


# 选择模型接口：设置/切换使用的模型
@router.post(
    "/model/select",
    response_model=SelectModelResponse,
    tags=["历史与模型"],
    summary="选择模型",
    description="切换当前使用的模型，后续聊天请求默认使用该模型。",
)
def select_model_api(request: SelectModelRequest) -> SelectModelResponse:
    try:
        return select_model(request.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

