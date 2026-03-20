from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    database_url_direct: str = Field(alias="DATABASE_URL_DIRECT")
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias=AliasChoices("GROQ_LLM_MODEL", "GROQ_MODEL"),
    )
    groq_llm_model_fallback: str = Field(
        default="llama-3.1-8b-instant",
        validation_alias=AliasChoices("GROQ_LLM_MODEL_FALLBACK", "GROQ_FALLBACK_MODEL"),
    )
    embedding_model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        validation_alias=AliasChoices("EMBEDDING_MODEL", "OPENAI_EMBED_MODEL"),
    )
    embedding_dimensions: int = Field(default=384, alias="EMBEDDING_DIMENSIONS")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    supabase_service_role_key: str = Field(default="", alias="SUPABASE_SERVICE_ROLE_KEY")
    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_anon_key: str = Field(default="", alias="SUPABASE_ANON_KEY")
    supabase_jwt_secret: str = Field(default="", alias="SUPABASE_JWT_SECRET")

    internal_service_api_key: str = Field(
        default="internal-secret-change-in-production",
        alias="INTERNAL_SERVICE_API_KEY",
    )

    api_key_prefix: str = Field(default="crm_", alias="API_KEY_PREFIX")
    api_key_length: int = Field(default=32, alias="API_KEY_LENGTH")

    api_key: str = Field(alias="API_KEY")
    environment: str = Field(default="local", alias="ENVIRONMENT")

    respect_robots_txt: bool = Field(default=True, alias="RESPECT_ROBOTS_TXT")
    crawl_min_delay_seconds: float = Field(default=3.0, alias="CRAWL_MIN_DELAY_SECONDS")
    crawl_max_attempts: int = Field(default=3, alias="CRAWL_MAX_ATTEMPTS")
    crawl_timeout_ms: int = Field(default=15000, alias="CRAWL_TIMEOUT_MS")
    crawl_use_browser_domains: str = Field(default="", alias="CRAWL_USE_BROWSER_DOMAINS")

    top_k_retrieval: int = Field(default=20, alias="TOP_K_RETRIEVAL")
    top_k_final: int = Field(default=8, alias="TOP_K_FINAL")
    max_top_k: int = Field(default=50, alias="MAX_TOP_K")
    min_similarity: float = Field(default=0.3, alias="MIN_SIMILARITY")

    cache_ttl_seconds: int = Field(default=3600, alias="CACHE_TTL_SECONDS")

    db_pool_min_size: int = Field(default=1, alias="DB_POOL_MIN_SIZE")
    db_pool_max_size: int = Field(default=5, alias="DB_POOL_MAX_SIZE")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="text", alias="LOG_FORMAT")


settings = Settings()
