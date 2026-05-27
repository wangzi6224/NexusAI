from fastapi import APIRouter

from src.app.api.routers import ROUTERS

router = APIRouter()

for api_router in ROUTERS:
    router.include_router(api_router)

__all__ = ["router"]
