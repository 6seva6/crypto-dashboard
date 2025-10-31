# scripts/debug_binance.py
import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import websockets
from app.logger_config import setup_loggers

setup_loggers()  # ← вызываем настройку логеров
logger = logging.getLogger(__name__)

async def test_binance_ws():
    url = "wss://stream.binance.com:9443/ws/btcusdt@depth20"
    try:
        async with websockets.connect(url) as ws:
            msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            logger.info("✅ Получено сообщение от Binance")
            logger.debug(f"Данные: {msg[:100]}...")
    except Exception as e:
        logger.error(f"❌ Ошибка WebSocket: {e}")

if __name__ == "__main__":
    import logging
    asyncio.run(test_binance_ws())