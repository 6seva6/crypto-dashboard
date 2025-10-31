# app/logger_config.py
import logging

def setup_loggers():
    # Базовая настройка
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Настройка уровней для разных модулей
    logging.getLogger("app.collectors").setLevel(logging.DEBUG)     # Подробные логи
    logging.getLogger("app.storage").setLevel(logging.WARNING)      # Только предупреждения
    logging.getLogger("app.api").setLevel(logging.INFO)             # Стандартный уровень
    logging.getLogger("app.processors").setLevel(logging.INFO)      # Стандартный уровень

    # Уровень для сторонних библиотек
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)