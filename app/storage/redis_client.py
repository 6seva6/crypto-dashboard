# app/storage/redis_client.py
import redis.asyncio as redis
import logging
from app.settings import settings

logger = logging.getLogger(__name__)  # ← будет "app.storage.redis_client"

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

async def test_connection():
    try:
        await redis_client.ping()
        logger.info("Redis connected")
    except Exception:
        logger.error("Redis connection failed")