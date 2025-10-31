# app/api/routes.py
import json
import logging
from fastapi import APIRouter, Query
from app.processors.orderbook import filter_orderbook
from app.processors.cluster import cluster_orderbook
from app.settings import settings
from app.collectors.binance_full import orderbook_states

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/api/orderbook")
async def get_orderbook(
    exchange: str = "binance",
    symbol: str = "BTCUSDT",
    min_size: float = None,
    min_volume_usdt: float = 100
):
    if min_size is None:
        min_size = settings.min_order_size

    # Получаем стакан из глобального хранилища
    state = orderbook_states.get(symbol)
    if not state:
        logger.warning(f"No state for {symbol}")
        return {"error": "No data yet"}

    raw_snapshot = await state.get_snapshot()

    # Форматируем как в старом коде для совместимости с filter_orderbook
    raw_data = {
        "bids": [[str(p), str(q)] for p, q in raw_snapshot["bids"]],
        "asks": [[str(p), str(q)] for p, q in raw_snapshot["asks"]]
    }

    # Фильтрация по минимальному объёму (в биткоинах)
    filtered = filter_orderbook(json.dumps(raw_data), min_size)

    # Кластеризация
    clustered = cluster_orderbook(filtered["bids"], filtered["asks"], min_volume_usdt)

    logger.info(f"Orderbook for {symbol} retrieved and clustered")
    return {
        "exchange": exchange,
        "symbol": symbol,
        "min_size": min_size,
        "min_volume_usdt": min_volume_usdt,
        "orderbook": clustered
    }