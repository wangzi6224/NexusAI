from functools import lru_cache

from pydantic import Field
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
        env_file=".env",
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
