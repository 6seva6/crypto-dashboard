# app/processors/orderbook.py
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def filter_orderbook(raw_data: str, min_size: float = 0.001) -> Dict[str, Any]:
    try:
        data = json.loads(raw_data)
        bids = [[p, q] for p, q in data.get("bids", []) if float(q) >= min_size]
        asks = [[p, q] for p, q in data.get("asks", []) if float(q) >= min_size]
        logger.debug(f"Filtered orderbook: {len(bids)} bids, {len(asks)} asks")
        return {"bids": bids, "asks": asks}
    except Exception as e:
        logger.error(f"Filter error: {e}")
        return {"bids": [], "asks": []}