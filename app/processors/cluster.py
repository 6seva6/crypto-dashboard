# app/processors/cluster.py
import logging
from typing import List, Dict, Any

# Создаём логер для этого модуля
logger = logging.getLogger(__name__)

def cluster_orderbook(bids: List[List[str]], asks: List[List[str]], min_volume_usdt: float = 10000) -> Dict[str, Any]:
    """
    Кластеризует стакан: объединяет близкие цены с маленьким объёмом.
    Адаптивный шаг: чем дальше от mid_price — тем крупнее шаг.
    """
    logger.debug(f"Начинаю кластеризацию стакана. Bids: {len(bids)}, Asks: {len(asks)}")

    if not bids or not asks:
        logger.warning("Пустой стакан: bids или asks отсутствуют.")
        return {"bids": [], "asks": []}

    # Рассчитываем mid_price
    try:
        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])
        mid_price = (best_bid + best_ask) / 2
        logger.debug(f"Mid-price рассчитан: {mid_price}")
    except (IndexError, ValueError) as e:
        logger.error(f"Ошибка при расчете mid-price: {e}")
        return {"bids": [], "asks": []}

    # Функция для расчёта шага агрегации
    def get_bucket_size(price: float) -> float:
        distance = abs(price - mid_price)
        # Чем дальше — тем крупнее шаг
        base_step = 1000  # базовый шаг
        if distance < 5000:
            bucket_size = base_step
        elif distance < 20000:
            bucket_size = base_step * 2
        else:
            bucket_size = base_step * 4

        logger.debug(f"Для цены {price} (расстояние {distance}) выбран шаг: {bucket_size}")
        return bucket_size

    # Обработка BID (покупатели)
    clustered_bids = []
    current_bucket = None
    bucket_size = 0

    for price_str, qty_str in bids:
        try:
            price = float(price_str)
            qty = float(qty_str)
        except ValueError as e:
            logger.warning(f"Некорректные данные в bids: {price_str}, {qty_str}. Пропущено. Ошибка: {e}")
            continue

        # Рассчитываем стоимость в USDT (если цена в USDT)
        volume_usdt = price * qty

        # Пропускаем маленькие объёмы
        if volume_usdt < min_volume_usdt:
            logger.debug(f"Пропускаю bid {price} x {qty} (объём {volume_usdt:.2f} < {min_volume_usdt})")
            continue

        logger.debug(f"Обрабатываю bid {price} x {qty}, объём {volume_usdt:.2f}")

        # Определяем размер бакета для этой цены
        bucket_size = get_bucket_size(price)

        # Округляем цену до ближайшего бакета
        rounded_price = round(price / bucket_size) * bucket_size

        # Если новый бакет — добавляем предыдущий
        if current_bucket is None or current_bucket["price"] != rounded_price:
            if current_bucket:
                logger.debug(f"Добавляю бакет bid: {current_bucket}")
                clustered_bids.append(current_bucket)
            current_bucket = {
                "price": rounded_price,
                "amount": qty,
                "volume_usdt": volume_usdt
            }
            logger.debug(f"Начинаю новый бакет bid: {current_bucket}")
        else:
            # Суммируем объём в текущем бакете
            current_bucket["amount"] += qty
            current_bucket["volume_usdt"] += volume_usdt
            logger.debug(f"Добавляю к существующему бакету bid: {current_bucket}")

    if current_bucket:
        logger.debug(f"Добавляю последний бакет bid: {current_bucket}")
        clustered_bids.append(current_bucket)

    # Обработка ASK (продавцы) — аналогично
    clustered_asks = []
    current_bucket = None
    bucket_size = 0

    for price_str, qty_str in asks:
        try:
            price = float(price_str)
            qty = float(qty_str)
        except ValueError as e:
            logger.warning(f"Некорректные данные в asks: {price_str}, {qty_str}. Пропущено. Ошибка: {e}")
            continue

        volume_usdt = price * qty

        if volume_usdt < min_volume_usdt:
            logger.debug(f"Пропускаю ask {price} x {qty} (объём {volume_usdt:.2f} < {min_volume_usdt})")
            continue

        logger.debug(f"Обрабатываю ask {price} x {qty}, объём {volume_usdt:.2f}")

        bucket_size = get_bucket_size(price)
        rounded_price = round(price / bucket_size) * bucket_size

        if current_bucket is None or current_bucket["price"] != rounded_price:
            if current_bucket:
                logger.debug(f"Добавляю бакет ask: {current_bucket}")
                clustered_asks.append(current_bucket)
            current_bucket = {
                "price": rounded_price,
                "amount": qty,
                "volume_usdt": volume_usdt
            }
            logger.debug(f"Начинаю новый бакет ask: {current_bucket}")
        else:
            current_bucket["amount"] += qty
            current_bucket["volume_usdt"] += volume_usdt
            logger.debug(f"Добавляю к существующему бакету ask: {current_bucket}")

    if current_bucket:
        logger.debug(f"Добавляю последний бакет ask: {current_bucket}")
        clustered_asks.append(current_bucket)

    # Сортируем: BID — по убыванию, ASK — по возрастанию
    clustered_bids.sort(key=lambda x: x["price"], reverse=True)
    clustered_asks.sort(key=lambda x: x["price"])

    logger.info(f"Кластеризация завершена: {len(clustered_bids)} кластеров bids, {len(clustered_asks)} кластеров asks")
    return {
        "bids": clustered_bids,
        "asks": clustered_asks
    }