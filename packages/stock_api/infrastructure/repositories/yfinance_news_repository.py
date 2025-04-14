import uuid
import yfinance as yf
from datetime import datetime, date
from typing import List, Optional
from stock_api.domain.news import News
from stock_api.domain.news_repository import NewsRepository
from stock_api.domain.prediction import Prediction


class YFinanceNewsRepository(NewsRepository):
    def add_news(self, news: News):
        pass

    def get_latest_news(self, ticker: str) -> Optional[News]:
        ticker_upper = ticker.upper()
        stock = yf.Ticker(ticker_upper)
        news_list = stock.news or []
        print(f"Raw news list for {ticker_upper}: {news_list}")
        news_objects = []
        for item in news_list:
            content = item.get("content", {})
            pub_date_str = content.get("pubDate")
            if not pub_date_str:
                print("Skipping item, no pubDate found:", item)
                continue
            try:
                pub_datetime = datetime.strptime(pub_date_str, "%Y-%m-%dT%H:%M:%SZ")
            except Exception as e:
                print(
                    f"Error parsing pubDate '{pub_date_str}' for item {item.get('id')}: {e}"
                )
                continue

            title = content.get("title", "")
            url = content.get("previewUrl")
            if not url:
                url = content.get("canonicalUrl", {}).get("url", "")

            news_objects.append(
                News(
                    id=item.get("id", str(uuid.uuid4())),
                    ticker=ticker_upper,
                    date=pub_datetime,
                    title=title,
                    url=url,
                    prediction=Prediction(
                        score=0, interpretation="No prediction", percentage_range="N/A"
                    ),
                )
            )
            print(f"Processed news item: '{title}' published at {pub_datetime}")

        if not news_objects:
            print("No valid news objects were created for ticker", ticker_upper)
            return None

        latest_news = max(news_objects, key=lambda n: n.date)
        print("Latest news object:", latest_news)
        return latest_news

    def get_news_by_date(self, ticker: str, news_date: date) -> List[News]:
        return []
