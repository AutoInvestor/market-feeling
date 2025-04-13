from datetime import date
from typing import List, Optional
from stock_api.domain.news import News
from stock_api.domain.news_repository import NewsRepository


class InMemoryNewsRepository(NewsRepository):
    def __init__(self):
        self.news_items: List[News] = []

    def add_news(self, news: News):
        self.news_items.append(news)

    def get_latest_news(self, ticker: str) -> Optional[News]:
        ticker = ticker.upper()
        filtered = [n for n in self.news_items if n.ticker == ticker]
        if not filtered:
            return None
        return max(filtered, key=lambda n: n.date)

    def get_news_by_date(self, ticker: str, news_date: date) -> List[News]:
        ticker = ticker.upper()
        return [
            n for n in self.news_items if n.ticker == ticker and n.date == news_date
        ]
