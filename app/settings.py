# app/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379/0"
    default_symbol: str = "BTCUSDT"
    min_order_size: float = 0.001

    class Config:
        env_file = ".env"

settings = Settings()