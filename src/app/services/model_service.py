from src.app.health import get_available_models
from src.app.runtime_config import get_selected_model, set_selected_model
from src.app.schemas import ModelsResponse, SelectModelResponse


def get_models() -> ModelsResponse:
    return ModelsResponse(
        current_model=get_selected_model(),
        available_models=get_available_models(),
    )


def select_model(model: str) -> SelectModelResponse:
    available_models = get_available_models()

    if model not in available_models:
        raise ValueError(f"模型不存在: {model}")

    set_selected_model(model)

    return SelectModelResponse(
        success=True,
        selected_model=model,
        message="模型切换成功",
    )
