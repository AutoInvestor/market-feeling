from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List
from stock_api.application.news.dtos import LatestNews


class NewsReadModelRepository(ABC):
    @abstractmethod
    def get(self, news_id: str) -> Optional[LatestNews]:
        pass

    @abstractmethod
    def save(self, latest_news: LatestNews) -> None:
        pass

    @abstractmethod
    def get_by_date_range(
        self, ticker: str, start_date: date, end_date: date
    ) -> List[LatestNews]:
        pass
