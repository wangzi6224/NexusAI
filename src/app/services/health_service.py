from src.app.health import check_ollama_model_exists, check_ollama_server
from src.app.schemas.schemas import HealthResponse


def get_health_status() -> HealthResponse:
    ok, message = check_ollama_server()
    if not ok:
        return HealthResponse(ok=False, message=message)

    ok, message = check_ollama_model_exists()
    if not ok:
        return HealthResponse(ok=False, message=message)

    return HealthResponse(ok=True, message="服务和模型均正常")
