from datetime import datetime, timedelta, time, date
from typing import List
from uuid import uuid4

from stock_api.application.news.latest_news_dto import LatestNews
from stock_api.application.news.news_read_model_repository import (
    NewsReadModelRepository,
)


class InMemoryNewsReadModelRepository(NewsReadModelRepository):
    def __init__(self) -> None:
        self._storage: dict[str, LatestNews] = {}

        now = datetime.utcnow().replace(microsecond=0)
        delta = timedelta(days=1)

        seed_data = [
            # Apple -----------------------------------------------------------------
            LatestNews(
                id=str(uuid4()),
                ticker="AAPL",
                date=now - delta,
                title="Apple reports record Q2 2025 earnings",
                url="https://example.com/news/apple-q2-2025-earnings",
                feeling=1,
            ),
            LatestNews(
                id=str(uuid4()),
                ticker="AAPL",
                date=now - 3 * delta,
                title="Apple unveils M4 chip for Macs at Spring Event",
                url="https://example.com/news/apple-m4-chip-launch",
                feeling=1,
            ),
            # Microsoft --------------------------------------------------------------
            LatestNews(
                id=str(uuid4()),
                ticker="MSFT",
                date=now - 2 * delta,
                title="Microsoft announces new Copilot features for Office 365",
                url="https://example.com/news/microsoft-copilot-office",
                feeling=1,
            ),
            # Amazon ----------------------------------------------------------------
            LatestNews(
                id=str(uuid4()),
                ticker="AMZN",
                date=now - 4 * delta,
                title="Amazon to expand same‑day delivery to 12 more cities",
                url="https://example.com/news/amazon-same-day-expansion",
                feeling=0,
            ),
            # NVIDIA ----------------------------------------------------------------
            LatestNews(
                id=str(uuid4()),
                ticker="NVDA",
                date=now - delta // 2,  # a few hours ago
                title="NVIDIA showcases next‑gen GPU architecture at GTC 2025",
                url="https://example.com/news/nvidia-gtc-2025",
                feeling=1,
            ),
        ]

        for item in seed_data:
            self.save(item)

    def get(self, news_id: str):
        return self._storage.get(news_id)

    def save(self, latest_news: LatestNews) -> None:
        self._storage[latest_news.id] = latest_news

    def get_by_date_range(
        self, ticker: str, start_date: date, end_date: date
    ) -> List[LatestNews]:
        results: List[LatestNews] = []

        for news in self._storage.values():
            if news.ticker != ticker:
                continue

            ndate = news.date.date() if isinstance(news.date, datetime) else news.date
            if start_date <= ndate <= end_date:
                results.append(news)

        results.sort(key=lambda n: n.date)
        return results

    def get_latest_news_for_ticker(self, ticker: str, limit: int) -> List[LatestNews]:
        if limit < 1:
            return []
        limit = min(limit, 50)

        def _to_datetime(d):
            if isinstance(d, datetime):
                return d
            return datetime.combine(d, time.min)

        matches = [news for news in self._storage.values() if news.ticker == ticker]
        matches.sort(key=lambda n: _to_datetime(n.date), reverse=True)

        return matches[:limit]
