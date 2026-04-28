# Application-specific exceptions
class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        detail: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail

# LLM错误
class LLMProviderError(AppError):
    def __init__(
        self,
        message: str = "模型服务调用失败",
        detail: str | None = None,
        status_code: int = 502,
    ) -> None:
        super().__init__(
            code="LLM_PROVIDER_ERROR",
            message=message,
            status_code=status_code,
            detail=detail,
        )


# 配置错误
class ConfigError(AppError):
    def __init__(
        self,
        message: str = "应用配置错误",
        detail: str | None = None,
        status_code: int = 500,
    ) -> None:
        super().__init__(
            code="CONFIG_ERROR",
            message=message,
            status_code=status_code,
            detail=detail,
        )
