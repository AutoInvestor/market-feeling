from stock_api.application.news.dtos import LatestNews
from stock_api.application.news.latest_news_read_model_repository import (
    LatestNewsReadModelRepository,
)

class InMemoryLatestNewsReadModelRepository(LatestNewsReadModelRepository):
    def __init__(self):
        self._storage: dict[str, LatestNews] = {}

    def get(self, ticker: str):
        return self._storage.get(ticker.upper())

    def save(self, latest_news: LatestNews) -> None:
        self._storage[latest_news.ticker.upper()] = latest_news
