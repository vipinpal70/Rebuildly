"""Tiny async Redis cache helper. Degrades gracefully to a no-op if Redis is
unavailable so the API never hard-fails on a cache miss/outage."""
import json
from typing import Any, Optional

import redis.asyncio as aioredis

from config.settings import settings
from src.utils.logger import logger

_client: Optional[aioredis.Redis] = None


def _get_client() -> Optional[aioredis.Redis]:
    global _client
    if _client is None:
        try:
            _client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:  # pragma: no cover
            logger.warning(f"Redis unavailable, caching disabled: {e}")
            _client = None
    return _client


async def cache_get(key: str) -> Optional[Any]:
    client = _get_client()
    if not client:
        return None
    try:
        raw = await client.get(key)
        return json.loads(raw) if raw else None
    except Exception as e:
        logger.warning(f"cache_get failed for {key}: {e}")
        return None


async def cache_set(key: str, value: Any, ttl: int = 60) -> None:
    client = _get_client()
    if not client:
        return
    try:
        await client.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as e:
        logger.warning(f"cache_set failed for {key}: {e}")


async def cache_delete_prefix(prefix: str) -> None:
    """Invalidate all keys under a prefix (used after mutations)."""
    client = _get_client()
    if not client:
        return
    try:
        async for k in client.scan_iter(match=f"{prefix}*"):
            await client.delete(k)
    except Exception as e:
        logger.warning(f"cache_delete_prefix failed for {prefix}: {e}")
