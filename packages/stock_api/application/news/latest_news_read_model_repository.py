from abc import ABC, abstractmethod
from typing import Optional
from stock_api.application.news.dtos import LatestNews

class LatestNewsReadModelRepository(ABC):
    @abstractmethod
    def get(self, ticker: str) -> Optional[LatestNews]:
        pass

    @abstractmethod
    def save(self, latest_news: LatestNews) -> None:
        pass
