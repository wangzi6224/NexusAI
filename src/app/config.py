from functools import lru_cache
import os
from typing import Any

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Settings 类用于统一管理应用配置，按功能类别分组，支持从 .env 或环境变量加载。
class Settings(BaseSettings):
    # 应用级配置：运行环境、日志级别、聊天记录存储路径
    app_env: str = Field(default="development", alias="APP_ENV")
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")
    chat_history_path: str = Field(
        default="chat_history.json",
        alias="CHAT_HISTORY_PATH",
    )

    # Ollama 相关配置：LLM 服务地址、模型与请求行为
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )
    ollama_model: str = Field(
        default="gemma4:e2b",
        alias="OLLAMA_MODEL",
    )
    ollama_timeout: int = Field(
        default=1200,
        alias="OLLAMA_TIMEOUT",
    )
    ollama_keep_alive: str = Field(
        default="5m",
        alias="OLLAMA_KEEP_ALIVE",
    )

    # LLM Provider 选择：顶层只区分本地 Ollama 与云端 OpenAI 兼容服务
    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")
    cloud_provider: str = Field(default="deepseek", alias="CLOUD_PROVIDER")

    # DeepSeek 线上 API 配置，兼容 OpenAI Chat Completions 接口
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        alias="DEEPSEEK_BASE_URL",
    )
    deepseek_api_key: str = Field(
        default=os.getenv("ANTHROPIC_AUTH_TOKEN", ""),
        validation_alias=AliasChoices("DEEPSEEK_API_KEY", "ANTHROPIC_AUTH_TOKEN"),
    )
    deepseek_model: str = Field(
        default="deepseek-v4-flash",
        alias="DEEPSEEK_MODEL",
    )
    deepseek_timeout: int = Field(default=120, alias="DEEPSEEK_TIMEOUT")
    deepseek_thinking_enabled: bool = Field(
        default=False,
        alias="DEEPSEEK_THINKING_ENABLED",
    )
    qwen_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        alias="QWEN_BASE_URL",
    )
    qwen_api_key: str = Field(
        default=os.getenv("QWEN_API_KEY", ""),
    )
    qwen_model: str = Field(default="qwen3.7-max", alias="QWEN_MODEL")
    qwen_timeout: int = Field(default=120, alias="QWEN_TIMEOUT")
    glm_base_url: str = Field(
        default="https://api.z.ai/api/paas/v4",
        validation_alias=AliasChoices("GLM_BASE_URL", "GML_BASE_URL"),
    )
    glm_api_key: str = Field(
        default="",
        validation_alias=AliasChoices(
            "GLM_API_KEY",
            "ZAI_API_KEY",
            "ZHIPUAI_API_KEY",
            "GML_API_KEY",
        ),
    )
    glm_model: str = Field(
        default="GLM-5.1",
        validation_alias=AliasChoices("GLM_MODEL", "GML_MODEL"),
    )
    glm_timeout: int = Field(
        default=120,
        validation_alias=AliasChoices("GLM_TIMEOUT", "GML_TIMEOUT"),
    )

    # PostgreSQL 数据库配置
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="ai_backend", alias="POSTGRES_DB")
    postgres_user: str = Field(default="wangzilong", alias="POSTGRES_USER")
    postgres_password: str = Field(
        default="ai_backend_password",
        alias="POSTGRES_PASSWORD",
    )

    # Embedding 相关配置
    embedding_model: str = Field(
        default="intfloat/multilingual-e5-base",
        alias="EMBEDDING_MODEL",
    )
    embedding_batch_size: int = Field(default=1500, alias="EMBEDDING_BATCH_SIZE")
    embedding_dimension: int = Field(default=768, alias="EMBEDDING_DIMENSION")

    # Reranker / RAG 相关配置
    reranker_enabled: bool = Field(default=True, alias="RERANKER_ENABLED")
    reranker_model: str = Field(
        default="BAAI/bge-reranker-base",
        alias="RERANKER_MODEL",
    )
    reranker_use_fp16: bool = Field(default=False, alias="RERANKER_USE_FP16")

    rag_candidate_k: int = Field(default=30, alias="RAG_CANDIDATE_K")
    rag_rerank_top_n: int = Field(default=5, alias="RAG_RERANK_TOP_N")
    rag_max_rerank_content_chars: int = Field(
        default=1200,
        alias="RAG_MAX_RERANK_CONTENT_CHARS",
    )

    rag_default_retrieval_mode: str = Field(
        default="vector_rerank",
        alias="RAG_DEFAULT_RETRIEVAL_MODE",
    )
    rag_vector_top_k: int = Field(default=30, alias="RAG_VECTOR_TOP_K")
    rag_keyword_top_k: int = Field(default=30, alias="RAG_KEYWORD_TOP_K")
    rag_fusion_top_k: int = Field(default=20, alias="RAG_FUSION_TOP_K")
    rag_rrf_k: int = Field(default=60, alias="RAG_RRF_K")
    rag_mmr_enabled: bool = Field(default=True, alias="RAG_MMR_ENABLED")
    rag_mmr_lambda: float = Field(default=0.7, alias="RAG_MMR_LAMBDA")
    agent_planner_type: str = Field(default="llm", alias="AGENT_PLANNER_TYPE")
    agent_planner_temperature: float = Field(
        default=0.0, alias="AGENT_PLANNER_TEMPERATURE"
    )
    agent_planner_timeout_seconds: int = Field(
        default=8, alias="AGENT_PLANNER_TIMEOUT_SECONDS"
    )

    # Agent 工具调用相关配置
    agent_allowed_tools: str = Field(
        default="list_docs,search_docs,read_doc",
        alias="AGENT_ALLOWED_TOOLS",
    )
    agent_tool_timeout_seconds: int = Field(
        default=10,
        alias="AGENT_TOOL_TIMEOUT_SECONDS",
    )
    agent_max_tool_result_chars: int = Field(
        default=8000,
        alias="AGENT_MAX_TOOL_RESULT_CHARS",
    )

    model_config = SettingsConfigDict(
        env_file=[".env", ".env.api_keys"],
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """获取全局 Settings 实例并缓存，避免重复读取环境变量。"""
    return Settings()


# Ollama / LLM 相关函数
def get_ollama_base_url() -> str:
    """返回 Ollama API 基础 URL，去除末尾斜杠。"""
    return get_settings().ollama_base_url.rstrip("/")


def get_ollama_model() -> str:
    """返回当前使用的 Ollama 模型名称。"""
    return get_settings().ollama_model


def get_ollama_timeout() -> int:
    """返回 Ollama 请求超时时间（秒）。"""
    return get_settings().ollama_timeout


def get_ollama_keep_alive() -> str:
    """返回 Ollama keep-alive 配置。"""
    return get_settings().ollama_keep_alive


def get_supported_llm_providers() -> list[str]:
    """返回当前代码支持的 LLM Provider 列表。"""
    return ["ollama", "cloud"]


def get_supported_cloud_providers() -> list[str]:
    """返回云端 OpenAI 兼容模型供应商列表。"""
    return ["deepseek", "qwen", "glm"]


def normalize_llm_provider(provider: str | None) -> str:
    """归一化顶层 Provider 名称，并兼容旧的 deepseek 选项。"""
    provider_name = (provider or "ollama").lower().strip()
    if provider_name in {"deepseek", "qwen", "gml", "glm"}:
        return "cloud"
    return provider_name


def normalize_cloud_provider(cloud_provider: str | None) -> str:
    """归一化云端模型供应商名称。"""
    provider_name = (cloud_provider or "deepseek").lower().strip()
    if provider_name == "gml":
        return "glm"
    return provider_name


def get_llm_provider_name() -> str:
    """返回当前 LLM Provider 名称。"""
    try:
        from src.app.runtime_config import get_selected_provider

        return get_selected_provider()
    except Exception:
        return normalize_llm_provider(get_settings().llm_provider)


def get_cloud_provider_name() -> str:
    """返回当前 Cloud 下选中的供应商名称。"""
    try:
        from src.app.runtime_config import get_selected_cloud_provider

        return get_selected_cloud_provider()
    except Exception:
        return normalize_cloud_provider(get_settings().cloud_provider)


def get_default_llm_model(
    provider: str | None = None,
    cloud_provider: str | None = None,
) -> str:
    """返回当前 Provider 对应的默认模型名称。"""
    settings = get_settings()
    provider_name = normalize_llm_provider(provider or settings.llm_provider)

    if provider_name == "cloud":
        cloud_provider_name = normalize_cloud_provider(
            cloud_provider or settings.cloud_provider
        )
        if cloud_provider_name == "qwen":
            return settings.qwen_model
        if cloud_provider_name == "glm":
            return settings.glm_model
        return settings.deepseek_model

    return settings.ollama_model


def get_cloud_provider_config(cloud_provider: str | None = None) -> dict[str, Any]:
    """返回指定云端供应商的 OpenAI SDK 连接配置。"""
    settings = get_settings()
    provider_name = normalize_cloud_provider(
        cloud_provider or get_cloud_provider_name()
    )

    if provider_name == "qwen":
        return {
            "cloud_provider": "qwen",
            "display_name": "Qwen",
            "base_url": settings.qwen_base_url.rstrip("/"),
            "api_key": settings.qwen_api_key,
            "api_key_env": "QWEN_API_KEY",
            "model": settings.qwen_model,
            "timeout": settings.qwen_timeout,
            "thinking_enabled": False,
        }

    if provider_name == "glm":
        return {
            "cloud_provider": "glm",
            "display_name": "GLM",
            "base_url": settings.glm_base_url.rstrip("/"),
            "api_key": settings.glm_api_key,
            "api_key_env": "GLM_API_KEY",
            "model": settings.glm_model,
            "timeout": settings.glm_timeout,
            "thinking_enabled": False,
        }

    return {
        "cloud_provider": "deepseek",
        "display_name": "DeepSeek",
        "base_url": settings.deepseek_base_url.rstrip("/"),
        "api_key": settings.deepseek_api_key,
        "api_key_env": "DEEPSEEK_API_KEY",
        "model": settings.deepseek_model,
        "timeout": settings.deepseek_timeout,
        "thinking_enabled": settings.deepseek_thinking_enabled,
    }


def resolve_llm_model(
    model: str | None = None,
    stored_model: str | None = None,
    stored_provider: str | None = None,
    provider: str | None = None,
) -> str:
    """按当前 Provider 解析本次请求应使用的模型。"""
    if model:
        return model

    current_provider = normalize_llm_provider(provider or get_llm_provider_name())
    if stored_model and (not stored_provider or stored_provider == current_provider):
        return stored_model

    try:
        from src.app.runtime_config import get_selected_model

        return get_selected_model(current_provider)
    except Exception:
        return get_default_llm_model(current_provider)


# 应用级配置函数
def get_log_level() -> str:
    """返回当前日志级别。"""
    return get_settings().app_log_level


def get_chat_history_path() -> str:
    """返回聊天历史记录文件存储路径。"""
    return get_settings().chat_history_path


# Embedding 相关配置函数
def get_embedding_model() -> str:
    return get_settings().embedding_model


def get_embedding_batch_size() -> int:
    return get_settings().embedding_batch_size


def get_embedding_dimension() -> int:
    return get_settings().embedding_dimension


# Reranker / RAG 相关配置函数
def is_reranker_enabled() -> bool:
    return get_settings().reranker_enabled


def get_reranker_model() -> str:
    return get_settings().reranker_model


def get_reranker_use_fp16() -> bool:
    return get_settings().reranker_use_fp16


def get_rag_candidate_k() -> int:
    return get_settings().rag_candidate_k


def get_rag_rerank_top_n() -> int:
    return get_settings().rag_rerank_top_n


def get_rag_max_rerank_content_chars() -> int:
    return get_settings().rag_max_rerank_content_chars


def get_rag_default_retrieval_mode() -> str:
    return get_settings().rag_default_retrieval_mode


def get_rag_vector_top_k() -> int:
    return get_settings().rag_vector_top_k


def get_rag_keyword_top_k() -> int:
    return get_settings().rag_keyword_top_k


def get_rag_fusion_top_k() -> int:
    return get_settings().rag_fusion_top_k


def get_rag_rrf_k() -> int:
    return get_settings().rag_rrf_k


def is_rag_mmr_enabled() -> bool:
    return get_settings().rag_mmr_enabled


def get_rag_mmr_lambda() -> float:
    return get_settings().rag_mmr_lambda


# Agent 相关配置函数
def get_agent_allowed_tools() -> list[str]:
    raw = get_settings().agent_allowed_tools
    return [item.strip() for item in raw.split(",") if item.strip()]


def get_agent_tool_timeout_seconds() -> int:
    return get_settings().agent_tool_timeout_seconds


def get_agent_max_tool_result_chars() -> int:
    return get_settings().agent_max_tool_result_chars


def get_agent_planner_type() -> str:
    return get_settings().agent_planner_type.lower().strip()


def get_agent_planner_temperature() -> float:
    return get_settings().agent_planner_temperature


def get_agent_planner_timeout_seconds() -> int:
    return get_settings().agent_planner_timeout_seconds
