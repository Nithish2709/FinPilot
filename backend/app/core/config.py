from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application Settings powered by pydantic-settings."""

    APP_NAME: str = "finpilot-backend"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://finpilot_user:finpilot_password@localhost:5432/finpilot_db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Versioning Prefix
    API_V1_STR: str = "/api/v1"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]

    # Ingestion & Uploads
    UPLOAD_DIR: str = "storage/uploads"
    MAX_UPLOAD_SIZE_BYTES: int = 15 * 1024 * 1024  # 15 MB
    ALLOWED_EXTENSIONS: set[str] = {".csv", ".xlsx", ".pdf"}

    # Stage 5 Chat & Context Management
    CHAT_CONTEXT_MESSAGE_LIMIT: int = 20

    # Stage 6 RAG & pgvector Configuration
    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    RETRIEVAL_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.5

    # Stage 7 Local LLM + Tool-Calling Agent Configuration
    LLM_PROVIDER: str = "local"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:1.5b-instruct-q4_K_M"
    OLLAMA_TIMEOUT: float = 120.0
    LOCAL_LLM_MODEL: str = "qwen2.5:1.5b-instruct-q4_K_M"
    LOCAL_LLM_BASE_URL: Optional[str] = "http://localhost:11434"
    LOCAL_LLM_TIMEOUT: float = 120.0
    LOCAL_LLM_TEMPERATURE: float = 0.1
    LOCAL_LLM_MAX_TOKENS: int = 512
    MAX_TOOL_CALLS: int = 3
    MAX_PARSE_RETRIES: int = 2

    # Stage 8 API LLM Fallback + Reliability Configuration
    LLM_PRIMARY_PROVIDER: str = "local"
    API_FALLBACK_ENABLED: bool = True
    API_LLM_PROVIDER: str = "openai_compatible"
    API_LLM_MODEL: str = "gpt-3.5-turbo"
    API_LLM_API_KEY: Optional[str] = None
    API_LLM_BASE_URL: Optional[str] = "https://api.openai.com/v1"
    API_LLM_TIMEOUT: float = 30.0
    MAX_LOCAL_RETRIES: int = 2
    MAX_API_RETRIES: int = 1
    CIRCUIT_FAILURE_THRESHOLD: int = 3
    CIRCUIT_COOLDOWN_SECONDS: float = 30.0

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
