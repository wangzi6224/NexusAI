from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.app.paths import STATIC_DIR
from src.app.schemas.schemas import HealthResponse
from src.app.services.health_service import get_health_status

router = APIRouter()


# 首页路由：返回静态前端页面（index.html）
@router.get(
    "/",
    tags=["基础"],
    summary="返回首页",
    description="返回静态前端页面 index.html，用于打开本地 Web 界面。",
)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


# 健康检查接口：返回服务状态信息
@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["基础"],
    summary="健康检查",
    description="检查后端服务是否可用，并返回当前服务状态信息。",
)
def health_check() -> HealthResponse:
    return get_health_status()

