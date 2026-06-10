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
    REDIS_ENABLED: bool = False

    # External APIs
    GROQ_API_KEY: str = ""
    SEMANTIC_SCHOLAR_API_KEY: str = ""
    UNPAYWALL_EMAIL: str = ""

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:80",
        "http://localhost",
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


settings = Settings()
