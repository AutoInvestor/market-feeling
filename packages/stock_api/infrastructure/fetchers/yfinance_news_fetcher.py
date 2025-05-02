import uuid
import yfinance as yf
from datetime import datetime, date
from typing import List, Optional
from stock_api.domain.news import News
from stock_api.domain.news_fetcher import NewsFetcher


class YFinanceNewsFetcher(NewsFetcher):
    def make_deterministic_id(
        self, ticker: str, pub_datetime, title: str, url: str
    ) -> str:
        ticker_norm = ticker.upper().strip()
        date_norm = pub_datetime.isoformat()
        title_norm = title.strip()
        url_norm = url.strip()

        raw = "||".join([ticker_norm, date_norm, title_norm, url_norm])

        return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))

    def get_latest_news(self, ticker: str) -> Optional[News]:
        ticker_upper = ticker.upper()
        stock = yf.Ticker(ticker_upper)
        news_list = stock.news or []
        news_objects = []
        for item in news_list:
            content = item.get("content", {})
            pub_date_str = content.get("pubDate")
            if not pub_date_str:
                continue
            try:
                pub_datetime = datetime.strptime(pub_date_str, "%Y-%m-%dT%H:%M:%SZ")
            except Exception as e:
                continue

            title = content.get("title", "")
            url = content.get("previewUrl")
            if not url:
                url = content.get("canonicalUrl", {}).get("url", "")

            news_objects.append(
                News(
                    id=self.make_deterministic_id(
                        ticker_upper, pub_datetime, title, url
                    ),
                    ticker=ticker_upper,
                    date=pub_datetime,
                    title=title,
                    url=url,
                )
            )

        if not news_objects:
            return None

        latest_news = max(news_objects, key=lambda n: n.date)
        return latest_news

    def get_news_by_date(self, ticker: str, news_date: date) -> List[News]:
        return []
