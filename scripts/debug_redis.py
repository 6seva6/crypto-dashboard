# scripts/debug_redis.py
import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.storage.redis_client import redis_client
from app.logger_config import setup_loggers

setup_loggers()  # ← вызываем настройку логеров
logger = logging.getLogger(__name__)

async def test_redis():
    try:
        await redis_client.set("debug:test", "ok")
        value = await redis_client.get("debug:test")
        if value == "ok":
            logger.info("✅ Redis подключён и работает")
        else:
            logger.error("❌ Redis вернул неожиданное значение")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к Redis: {e}")

if __name__ == "__main__":
    import logging
    asyncio.run(test_redis())