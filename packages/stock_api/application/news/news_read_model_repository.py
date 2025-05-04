from abc import ABC, abstractmethod
from typing import Optional
from stock_api.application.news.dtos import LatestNews


class NewsReadModelRepository(ABC):
    @abstractmethod
    def get(self, news_id: str) -> Optional[LatestNews]:
        pass

    @abstractmethod
    def save(self, latest_news: LatestNews) -> None:
        pass
