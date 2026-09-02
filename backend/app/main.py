"""ResearchFinder - FastAPI Backend Entry Point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_tables, engine
from app.core.cache import init_redis
from app.routers import auth, papers, collections, bibliography, history, ai, upload, dashboard, payment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup — ensure all database tables are created (PostgreSQL & SQLite)
    logger.info("Initializing database tables...")
    await create_tables()
    logger.info("Database tables ready")

    # Run database & storage maintenance tasks
    try:
        from sqlalchemy import text
        from app.services.cleanup import purge_all_uploaded_papers, prune_stale_cache_papers, cleanup_orphan_files
        await purge_all_uploaded_papers()
        await prune_stale_cache_papers(days=14)
        await cleanup_orphan_files()
        async with engine.begin() as conn:
            await conn.execute(text("UPDATE users SET plan_tier = 'free', storage_quota_bytes = 104857600 WHERE email = 'ival@gmail.com';"))
        logger.info("Database and storage maintenance complete. Account ival@gmail.com reset to free plan.")
    except Exception as e:
        logger.warning(f"Maintenance task failed: {e}")

    await init_redis()

    _is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    logger.info(f"ResearchFinder API started (DB: {'SQLite' if _is_sqlite else 'PostgreSQL'})")
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="ResearchFinder API",
    description="AI-Powered Research Paper Finder & Summarizer",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(papers.router, prefix="/api/papers", tags=["Papers"])
app.include_router(collections.router, prefix="/api/collections", tags=["Collections"])
app.include_router(bibliography.router, prefix="/api/bibliography", tags=["Bibliography"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(payment.router, prefix="/api/payment", tags=["Payment"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "researchfinder"}
