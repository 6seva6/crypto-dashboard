# app/main.py
import asyncio
import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from app.api.routes import router
from app.collectors.binance_full import collect_full_orderbook
from app.logger import setup_loggers

templates = Jinja2Templates(directory="app/templates")

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_loggers()
    logger = logging.getLogger(__name__)
    logger.info("Starting background tasks...")
    task = asyncio.create_task(collect_full_orderbook())
    yield
    logger.info("Shutting down...")
    task.cancel()

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return templates.TemplateResponse("dashboard.html", {"request": {}})