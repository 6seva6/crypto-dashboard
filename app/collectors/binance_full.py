# app/collectors/binance_full.py
import asyncio
import json
import logging
import aiohttp
import websockets
from typing import Dict
from app.storage.orderbook_state import OrderBookState

logger = logging.getLogger(__name__)

BINANCE_REST_URL = "https://fapi.binance.com/fapi/v1/depth"
BINANCE_WS_URL = "wss://fstream.binance.com/ws/btcusdt@depth"

# Глобальное хранилище стаканов
orderbook_states: Dict[str, OrderBookState] = {}

async def fetch_snapshot(session: aiohttp.ClientSession, symbol: str):
    url = f"{BINANCE_REST_URL}?symbol={symbol}&limit=1000"  # Максимум 5000
    async with session.get(url) as resp:
        if resp.status == 200:
            data = await resp.json()
            logger.info(f"Fetched snapshot for {symbol}")
            return data
        else:
            logger.error(f"Failed to fetch snapshot for {symbol}: {resp.status}")
            return None

async def collect_full_orderbook():
    symbol = "BTCUSDT"
    state = OrderBookState(symbol)
    orderbook_states[symbol] = state

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Получаем снапшот
                snapshot = await fetch_snapshot(session, symbol)
                if not snapshot:
                    await asyncio.sleep(5)
                    continue

                await state.update_from_snapshot(snapshot)

                # Подключаемся к WebSocket и слушаем дельты
                logger.info(f"Connecting to WebSocket for {symbol}...")
                async with websockets.connect(BINANCE_WS_URL) as ws:
                    async for msg in ws:
                        delta = json.loads(msg)
                        await state.apply_delta(delta)

            except Exception as e:
                logger.error(f"Error in full collector for {symbol}: {e}")
                await asyncio.sleep(5)  # Ждём перед переподключением
