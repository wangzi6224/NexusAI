from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.app.logger import get_logger

logger = get_logger()


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("未处理异常: path=%s error=%s", request.url.path, exc)

        return JSONResponse(
            status_code=500,
            content={
                "detail": "服务器内部错误",
            },
        )
