# app/storage/orderbook_state.py
import asyncio
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class OrderBookState:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids: Dict[float, float] = {}  # {price: qty}
        self.asks: Dict[float, float] = {}  # {price: qty}
        self.last_update_id: Optional[int] = None
        self.lock = asyncio.Lock()

    async def update_from_snapshot(self, snapshot: Dict):
        """
        Обновляет стакан из снапшота (REST API).
        """
        async with self.lock:
            self.bids = {float(p): float(q) for p, q in snapshot.get("bids", [])}
            self.asks = {float(p): float(q) for p, q in snapshot.get("asks", [])}
            self.last_update_id = snapshot.get("lastUpdateId")
            logger.info(f"Updated {self.symbol} from snapshot: {len(self.bids)} bids, {len(self.asks)} asks")

    async def apply_delta(self, delta: Dict):
        """
        Применяет дельту (из WebSocket @depth).
        """
        async with self.lock:
            # Обновляем bids
            for price_str, qty_str in delta.get("b", []):
                price = float(price_str)
                qty = float(qty_str)
                if qty == 0:
                    self.bids.pop(price, None)  # Удаляем ордер
                else:
                    self.bids[price] = qty

            # Обновляем asks
            for price_str, qty_str in delta.get("a", []):
                price = float(price_str)
                qty = float(qty_str)
                if qty == 0:
                    self.asks.pop(price, None)  # Удаляем ордер
                else:
                    self.asks[price] = qty

            logger.debug(f"Applied delta to {self.symbol}: {len(self.bids)} bids, {len(self.asks)} asks")

    async def get_snapshot(self):
        """
        Возвращает текущий стакан (для API).
        """
        async with self.lock:
            return {
                "bids": sorted(self.bids.items(), key=lambda x: x[0], reverse=True),
                "asks": sorted(self.asks.items(), key=lambda x: x[0])
            }