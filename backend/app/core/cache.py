"""Redis cache connection and helpers. Gracefully handles missing Redis."""

import json
import logging

import redis.asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: aioredis.Redis | None = None
_redis_available: bool = False


async def init_redis() -> bool:
    """Initialize Redis connection. Returns True if connected."""
    global redis_client, _redis_available

    if not settings.REDIS_ENABLED or not settings.REDIS_URL:
        logger.info("Redis disabled (local dev mode)")
        _redis_available = False
        return False

    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
        await redis_client.ping()
        _redis_available = True
        logger.info("Redis connected")
        return True
    except Exception as e:
        logger.warning(f"Redis unavailable, caching disabled: {e}")
        redis_client = None
        _redis_available = False
        return False


async def cache_get(key: str) -> dict | list | None:
    """Get JSON-serializable value from cache. Returns None if Redis is down."""
    if not _redis_available or redis_client is None:
        return None
    try:
        raw = await redis_client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception:
        return None


async def cache_set(key: str, value: dict | list, ttl: int = 3600) -> None:
    """Set JSON-serializable value in cache. No-op if Redis is down."""
    if not _redis_available or redis_client is None:
        return
    try:
        await redis_client.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception:
        pass


async def cache_delete(key: str) -> None:
    """Delete a key from cache. No-op if Redis is down."""
    if not _redis_available or redis_client is None:
        return
    try:
        await redis_client.delete(key)
    except Exception:
        pass
