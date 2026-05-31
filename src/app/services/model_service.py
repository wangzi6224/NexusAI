from src.app.config import get_supported_llm_providers
from src.app.exceptions import LLMProviderError
from src.app.health import get_available_models
from src.app.runtime_config import (
    get_selected_model,
    get_selected_provider,
    set_selected_model,
)
from src.app.schemas.schemas import ModelsResponse, ProviderModels, SelectModelResponse


def get_models() -> ModelsResponse:
    current_provider = get_selected_provider()
    available_by_provider: dict[str, list[str]] = {}

    for provider in get_supported_llm_providers():
        try:
            available_by_provider[provider] = get_available_models(provider)
        except LLMProviderError:
            available_by_provider[provider] = []

    provider_models = [
        ProviderModels(
            provider=provider,
            current_model=get_selected_model(provider),
            available_models=available_by_provider[provider],
        )
        for provider in get_supported_llm_providers()
    ]

    return ModelsResponse(
        current_provider=current_provider,
        current_model=get_selected_model(current_provider),
        available_models=available_by_provider.get(current_provider, []),
        providers=provider_models,
    )


def select_model(model: str, provider: str | None = None) -> SelectModelResponse:
    provider_name = (provider or get_selected_provider()).lower().strip()
    available_models = get_available_models(provider_name)

    if model not in available_models:
        raise ValueError(f"模型不存在: {model}")

    set_selected_model(model, provider_name)

    return SelectModelResponse(
        success=True,
        selected_provider=provider_name,
        selected_model=model,
        message="模型切换成功",
    )
