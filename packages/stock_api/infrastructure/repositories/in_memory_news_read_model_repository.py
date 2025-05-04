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
