"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Load environment variables with defaults."""

    # App
    APP_NAME: str = "ResearchFinder"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-to-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database (SQLite for local dev, PostgreSQL for Docker/production)
    DATABASE_URL: str = "sqlite+aiosqlite:///./researchfinder.db"

    # Redis (optional for local dev, required for Docker/production)
    REDIS_URL: str = ""
    REDIS_ENABLED: bool = True

    # External APIs
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    SEMANTIC_SCHOLAR_API_KEY: str = ""
    UNPAYWALL_EMAIL: str = ""
    MAYAR_API_KEY: str = ""
    MAYAR_API_URL: str = "https://api.mayar.id/hl/v1/payment/create"
    MAYAR_WEBHOOK_TOKEN: str = ""

    # Midtrans Payment Gateway Configs
    MIDTRANS_SERVER_KEY: str = "SB-Mid-server-SampleServerKey123"
    MIDTRANS_CLIENT_KEY: str = "SB-Mid-client-SampleClientKey123"
    MIDTRANS_IS_PRODUCTION: bool = False

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:80",
        "http://localhost",
        "https://research.ivalpermana.my.id",
        "http://research.ivalpermana.my.id",
        "*",
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
