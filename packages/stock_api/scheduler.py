import asyncio
import os
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx

from stock_api.logger import get_logger

logger = get_logger(__name__)

# Base URL of the API (override via env var API_BASE)
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8080")

# Create the AsyncIO scheduler
scheduler = AsyncIOScheduler(timezone="UTC")

async def fetch_companies(client: httpx.AsyncClient) -> list[str]:
    """Fetches /companies and returns a list of tickers"""
    url = f"{API_BASE}/companies"
    resp = await client.get(url, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    return data.get("companies", [])

async def ping_latest_for_ticker(client: httpx.AsyncClient, ticker: str):
    """Pings /companies/{ticker}/news/latest and logs result"""
    url = f"{API_BASE}/companies/{ticker}/news/latest"
    try:
        r = await client.get(url, timeout=5)
        r.raise_for_status()
        logger.info("✅ %s → %s", ticker, r.status_code)
    except Exception as e:
        logger.error("❌ %s → %s", ticker, e)

async def ping_all_latest_news():
    """Fetches all tickers and pings their latest-news endpoint concurrently"""
    async with httpx.AsyncClient() as client:
        try:
            tickers = await fetch_companies(client)
            logger.info("Found %d companies, pinging latest-news…", len(tickers))
        except Exception as e:
            logger.error("Failed to fetch companies: %s", e)
            return

        tasks = [ping_latest_for_ticker(client, tk) for tk in tickers]
        await asyncio.gather(*tasks, return_exceptions=True)

def setup_scheduler(app: FastAPI):
    """Registers scheduler startup/shutdown events on the FastAPI app"""
    @app.on_event("startup")
    async def start_ping_scheduler():
        scheduler.add_job(ping_all_latest_news, trigger="cron", second=0)
        scheduler.start()
        logger.info("Scheduler started: ping all latest-news every minute.")

    @app.on_event("shutdown")
    async def stop_ping_scheduler():
        scheduler.shutdown()
