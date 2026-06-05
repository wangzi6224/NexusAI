from src.app.config import normalize_llm_provider
from src.app.runtime_config import get_selected_provider
from src.app.services.llm.base import LLMProvider
from src.app.services.llm.cloud_provider import CloudProvider
from src.app.services.llm.ollama_provider import OllamaProvider


def get_llm_provider(provider: str | None = None) -> LLMProvider:
    provider = normalize_llm_provider(provider or get_selected_provider())

    if provider == "cloud":
        return CloudProvider()

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(f"不支持的 LLM_PROVIDER: {provider}")
