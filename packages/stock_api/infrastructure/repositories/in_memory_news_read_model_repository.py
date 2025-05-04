from datetime import date, datetime
from typing import List

from stock_api.application.news.dtos import LatestNews
from stock_api.application.news.news_read_model_repository import (
    NewsReadModelRepository,
)


class InMemoryNewsReadModelRepository(NewsReadModelRepository):
    def __init__(self):
        self._storage: dict[str, LatestNews] = {}

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
