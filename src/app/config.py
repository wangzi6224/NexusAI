from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# 定义一个 Pydantic 模型类 Settings，用于存储应用程序的配置项
class Settings(BaseSettings):
    # APP_ENV: 环境变量，默认为 "development"，可选值包括 "development"、"production" 和 "testing"
    app_env: str = Field(default="development", alias="APP_ENV")

    # APP_LOG_LEVEL: 日志级别，默认为 "INFO"，可选值包括 "DEBUG"、"INFO"、"WARNING"、"ERROR" 和 "CRITICAL"
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")

    # OLLAMA_BASE_URL: Ollama API 的基础 URL，默认为 "http://localhost:11434"
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )

    # OLLAMA_MODEL: Ollama 模型名称，默认为 "gemma4:e2b"
    ollama_model: str = Field(
        default="gemma4:e2b",
        alias="OLLAMA_MODEL",
    )

    # OLLAMA_TIMEOUT: Ollama API 请求的超时时间，单位为秒，默认为 1200 秒（20 分钟）
    ollama_timeout: int = Field(
        default=1200,
        alias="OLLAMA_TIMEOUT",
    )

    # OLLAMA_KEEP_ALIVE: Ollama API 连接的 keep-alive 时间，默认为 "5m"（5 分钟）
    ollama_keep_alive: str = Field(
        default="5m",
        alias="OLLAMA_KEEP_ALIVE",
    )

    # CHAT_HISTORY_PATH: 聊天记录文件的路径，默认为 "chat_history.json"
    chat_history_path: str = Field(
        default="chat_history.json",
        alias="CHAT_HISTORY_PATH",
    )

    # 配置 Pydantic Settings 的相关选项，包括环境变量文件的路径和编码，以及额外字段的处理方式
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # PostgreSQL 配置
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="ai_backend", alias="POSTGRES_DB")
    postgres_user: str = Field(default="wangzilong", alias="POSTGRES_USER")
    postgres_password: str = Field(
        default="ai_backend_password",
        alias="POSTGRES_PASSWORD",
    )

    # Embedding 配置
    embedding_model: str = Field(
        default="intfloat/multilingual-e5-base",
        alias="EMBEDDING_MODEL",
    )
    embedding_batch_size: int = Field(default=1500, alias="EMBEDDING_BATCH_SIZE")
    embedding_dimension: int = Field(default=768, alias="EMBEDDING_DIMENSION")

    # Reranker 配置
    reranker_enabled: bool = Field(default=True, alias="RERANKER_ENABLED")
    reranker_model: str = Field(
        default="BAAI/bge-reranker-base", alias="RERANKER_MODEL"
    )
    reranker_use_fp16: bool = Field(default=False, alias="RERANKER_USE_FP16")
    rag_candidate_k: int = Field(default=30, alias="RAG_CANDIDATE_K")
    rag_rerank_top_n: int = Field(default=5, alias="RAG_RERANK_TOP_N")
    rag_max_rerank_content_chars: int = Field(
        default=1200, alias="RAG_MAX_RERANK_CONTENT_CHARS"
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


# 定义一个函数 get_settings，用于获取 Settings 实例，并使用 lru_cache 装饰器进行缓存，以提高性能
@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_ollama_base_url() -> str:
    return get_settings().ollama_base_url.rstrip("/")


def get_ollama_model() -> str:
    return get_settings().ollama_model


def get_ollama_timeout() -> int:
    return get_settings().ollama_timeout


def get_ollama_keep_alive() -> str:
    return get_settings().ollama_keep_alive


def get_log_level() -> str:
    return get_settings().app_log_level


def get_chat_history_path() -> str:
    return get_settings().chat_history_path


def get_embedding_model() -> str:
    return get_settings().embedding_model


def get_embedding_batch_size() -> int:
    return get_settings().embedding_batch_size


def get_embedding_dimension() -> int:
    return get_settings().embedding_dimension


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
