from datetime import datetime, date
from typing import Dict, List, Optional

from stock_api.domain.news import News
from stock_api.domain.news_fetcher import NewsFetcher


class InMemoryNewsFetcher(NewsFetcher):
    _news: Dict[str, List[News]] = {
        "NFLX": [
            News(
                id="NFLX-2024-04-06T12:00:00Z-1",
                ticker="NFLX",
                date=datetime(2024, 4, 6, 12, 0),
                title="Netflix hits new subscriber record",
                url="https://example.com/netflix-news1",
            ),
            News(
                id="NFLX-2024-04-07T09:30:00Z-2",
                ticker="NFLX",
                date=datetime(2024, 4, 7, 9, 30),
                title="Netflix announces price increase",
                url="https://example.com/netflix-news2",
            ),
        ],
    }

    def get_latest_news(self, ticker: str) -> Optional[News]:
        news_list = self._news.get(ticker.upper(), [])
        return news_list[-1] if news_list else None

    def get_news_by_date(self, ticker: str, news_date: date) -> List[News]:
        return [
            n for n in self._news.get(ticker.upper(), []) if n.date.date() == news_date
        ]
