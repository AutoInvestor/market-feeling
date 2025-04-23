from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from stock_api.domain.news import News


class NewsFetcher(ABC):
    @abstractmethod
    def get_latest_news(self, ticker: str) -> Optional[News]:
        pass

    @abstractmethod
    def get_news_by_date(self, ticker: str, news_date: date) -> List[News]:
        pass
