from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Rebuildly Engine"
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

    # Fernet key (urlsafe base64, 32 bytes) protecting API keys the admin saves in the
    # dashboard. Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    # If unset, a key is derived from ADMIN_SECRET — set this explicitly in production.
    SETTINGS_ENCRYPTION_KEY: Optional[str] = None

    # Database URIs
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/opportunity_finder"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Discovery & Auditor Controls
    DEFAULT_MAX_LEADS_PER_CITY: int = 50
    MIN_GOOGLE_RATING: float = 4.2
    MIN_REVIEW_COUNT: int = 30

    # Free data sources
    COMPANIES_HOUSE_API_KEY: Optional[str] = None  # https://developer.company-information.service.gov.uk
    # Comma-separated discovery sources used when a campaign doesn't specify any:
    # "google" (Places API, or the demo fallback without a key) and/or "osm".
    DISCOVERY_SOURCES: str = "google"
    # Fetch photos/hours/summary/newest reviews in the Places Details call so the GBP and
    # review detectors have data. These fields bill under higher Places SKUs (Contact /
    # Atmosphere) — set False to keep the cheaper Basic-only call.
    PLACES_FETCH_GBP_DETAILS: bool = True

    # Page-load limit for the mobile audit. 5s (the old hardcoded value) timed out on
    # most real small-business sites, which then looked 'inaccessible' and scored wrongly.
    AUDIT_NAVIGATION_TIMEOUT_MS: int = 20000

    # Signals
    SIGNALS_ENABLED: bool = True
    ACCESSIBILITY_AXE_ENABLED: bool = True  # launches a 2nd headless browser per lead
    ACCESSIBILITY_AXE_TIMEOUT_SECONDS: int = 20

    # Discovery Engine: concurrency & resilience
    DISCOVERY_MAX_CONCURRENT_QUERIES: int = 3  # parallel category x city x country queries
    PLACES_API_MAX_RETRIES: int = 3
    PLACES_API_RETRY_BASE_DELAY_SECONDS: float = 2.0  # exponential backoff: 2s, 4s, 8s...

    # Discovery Engine: API budget guardrail (Idea-plan.md Section 9 names Places API
    # cost as an explicit risk). Approximate per-call USD costs below are a rough
    # guardrail for spend estimation only, NOT a source of truth for billing — verify
    # against current Google Cloud Places API pricing before relying on the estimate.
    MAX_PLACES_API_CALLS_PER_JOB: int = 500
    PLACES_TEXT_SEARCH_COST_USD: float = 0.032
    PLACES_DETAILS_COST_USD: float = 0.017

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
