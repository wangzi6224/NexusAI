from src.app.config import (
    get_supported_cloud_providers,
    get_supported_llm_providers,
    normalize_cloud_provider,
    normalize_llm_provider,
)
from src.app.exceptions import LLMProviderError
from src.app.health import get_available_models
from src.app.runtime_config import (
    get_selected_cloud_provider,
    get_selected_model,
    get_selected_provider,
    set_selected_model,
)
from src.app.schemas.schemas import (
    CloudProviderModels,
    ModelsResponse,
    ProviderModels,
    SelectModelResponse,
)


def get_models() -> ModelsResponse:
    current_provider = get_selected_provider()
    current_cloud_provider = get_selected_cloud_provider()
    available_by_provider: dict[str, list[str]] = {}
    available_by_cloud_provider: dict[str, list[str]] = {}

    for provider in get_supported_llm_providers():
        try:
            available_by_provider[provider] = get_available_models(
                provider,
                cloud_provider=current_cloud_provider if provider == "cloud" else None,
            )
        except LLMProviderError:
            available_by_provider[provider] = []

    for cloud_provider in get_supported_cloud_providers():
        try:
            available_by_cloud_provider[cloud_provider] = get_available_models(
                "cloud",
                cloud_provider=cloud_provider,
            )
        except LLMProviderError:
            available_by_cloud_provider[cloud_provider] = []

    provider_models = [
        ProviderModels(
            provider=provider,
            current_model=get_selected_model(
                provider,
                current_cloud_provider if provider == "cloud" else None,
            ),
            available_models=available_by_provider[provider],
        )
        for provider in get_supported_llm_providers()
    ]
    cloud_provider_models = [
        CloudProviderModels(
            provider=cloud_provider,
            current_model=get_selected_model("cloud", cloud_provider),
            available_models=available_by_cloud_provider[cloud_provider],
        )
        for cloud_provider in get_supported_cloud_providers()
    ]

    return ModelsResponse(
        current_provider=current_provider,
        current_cloud_provider=current_cloud_provider,
        current_model=get_selected_model(current_provider, current_cloud_provider),
        available_models=available_by_provider.get(current_provider, []),
        providers=provider_models,
        cloud_providers=cloud_provider_models,
    )


def select_model(
    model: str,
    provider: str | None = None,
    cloud_provider: str | None = None,
) -> SelectModelResponse:
    provider_name = normalize_llm_provider(provider or get_selected_provider())
    cloud_provider_name = (
        normalize_cloud_provider(cloud_provider or get_selected_cloud_provider())
        if provider_name == "cloud"
        else None
    )
    available_models = get_available_models(provider_name, cloud_provider_name)

    if model not in available_models:
        raise ValueError(f"模型不存在: {model}")

    set_selected_model(model, provider_name, cloud_provider_name)

    return SelectModelResponse(
        success=True,
        selected_provider=provider_name,
        selected_cloud_provider=cloud_provider_name,
        selected_model=model,
        message="模型切换成功",
    )
