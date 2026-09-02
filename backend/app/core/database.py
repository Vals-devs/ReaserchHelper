"""Async database connection using SQLAlchemy."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy import text
from app.core.config import settings

# SQLite needs check_same_thread=False for async usage
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

_engine_kwargs: dict = {
    "echo": settings.DEBUG,
}

if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_pre_ping"] = True
    _engine_kwargs["pool_size"] = 10
    _engine_kwargs["max_overflow"] = 20
    _engine_kwargs["pool_timeout"] = 30
    _engine_kwargs["pool_recycle"] = 1800

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create all tables, ensure new columns exist, and create database performance indexes."""
    from app.models import Base  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for stmt in [
            "ALTER TABLE papers ADD COLUMN IF NOT EXISTS journal VARCHAR(255);",
            "ALTER TABLE papers ADD COLUMN IF NOT EXISTS accreditation VARCHAR(100);",
            "ALTER TABLE papers ADD COLUMN IF NOT EXISTS user_id VARCHAR(36);",
            "CREATE INDEX IF NOT EXISTS idx_papers_source_user ON papers(source, user_id);",
            "CREATE INDEX IF NOT EXISTS idx_papers_cached_at ON papers(cached_at);",
            "CREATE INDEX IF NOT EXISTS idx_search_history_user ON search_history(user_id, searched_at);",
        ]:
            try:
                await conn.execute(text(stmt))
            except Exception:
                pass
