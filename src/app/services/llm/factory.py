from src.app.runtime_config import get_selected_provider
from src.app.services.llm.base import LLMProvider
from src.app.services.llm.deepseek_provider import DeepSeekProvider
from src.app.services.llm.ollama_provider import OllamaProvider


def get_llm_provider(provider: str | None = None) -> LLMProvider:
    provider = (provider or get_selected_provider()).lower().strip()

    if provider == "deepseek":
        return DeepSeekProvider()

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(f"不支持的 LLM_PROVIDER: {provider}")
