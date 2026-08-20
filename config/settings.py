from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Opportunity Finder Engine"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # API Keys & Flexible LLM Settings
    GOOGLE_PLACES_API_KEY: Optional[str] = None
    PAGESPEED_API_KEY: Optional[str] = None
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    CLAUDE_API_KEY: Optional[str] = None

    # Flexible Open LLM Configuration
    LLM_PROVIDER: str = "anthropic"  # openai, groq, ollama, together, anthropic, custom
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: str = "claude-3-5-sonnet-20241022"

    # Database URIs
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/opportunity_finder"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Discovery & Auditor Controls
    DEFAULT_MAX_LEADS_PER_CITY: int = 50
    MIN_GOOGLE_RATING: float = 4.2
    MIN_REVIEW_COUNT: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
