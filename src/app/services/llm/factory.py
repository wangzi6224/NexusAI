from src.app.config import get_settings
from src.app.services.llm.base import LLMProvider
from src.app.services.llm.deepseek_provider import DeepSeekProvider
from src.app.services.llm.ollama_provider import OllamaProvider


def get_llm_provider() -> LLMProvider:
    provider = get_settings().llm_provider.lower().strip()

    if provider == "deepseek":
        return DeepSeekProvider()

    if provider == "ollama":
        return OllamaProvider()

    raise ValueError(f"不支持的 LLM_PROVIDER: {provider}")
