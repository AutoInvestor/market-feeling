import uuid
import requests
from urllib.parse import urlparse
from datetime import datetime, date
from typing import List, Optional
from stock_api.domain.news import News
from stock_api.domain.news_repository import NewsRepository
from stock_api.domain.prediction import Prediction

class YFinanceNewsRepository(NewsRepository):
    def add_news(self, news: News):
        # Implementation for storing news locally if needed.
        pass

    def get_latest_news(self, ticker: str) -> Optional[News]:
        # Existing implementation using yfinance.
        pass

    def get_news_by_date(self, ticker: str, news_date: date) -> List[News]:
        ticker_upper = ticker.upper()

        # Setup a requests session with a custom user agent
        GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
        session = requests.Session()
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/90.0.4430.85 Safari/537.36"
            )
        })

        def build_query(company_name: str) -> str:
            finance_domains_block = "domain:finance.yahoo.com"
            company_block = f'"{company_name}"'
            return f"{finance_domains_block} {company_block}"

        # Use ticker as company name for this example.
        company = {"ticker": ticker_upper, "name": ticker_upper}
        start_date_str = news_date.isoformat()   # Format: YYYY-MM-DD
        end_date_str = start_date_str

        # Build parameters for GDELT query.
        params = {
            "query": build_query(company["name"]),
            "mode": "artlist",
            "format": "json",
            "maxrecords": "250",
            "startdatetime": start_date_str.replace("-", "") + "000000",
            "enddatetime": end_date_str.replace("-", "") + "235959",
            "sort": "datedesc",
        }

        try:
            response = session.get(GDELT_URL, params=params)
            print(f"GDELT response status: {response.status_code}")
            # Check for specific error message before parsing JSON
            response_text = response.text.strip()
            if response_text.startswith("The specified phrase is too short"):
                print(f"GDELT returned error: {response_text}")
                articles = []
            else:
                try:
                    data = response.json()
                    articles = data.get("articles", [])
                except Exception as e:
                    print(f"JSON parsing failed. Response text: {response.text}")
                    raise e
        except Exception as ex:
            print(f"Failed to fetch articles for {company['ticker']} from {start_date_str} to {end_date_str}: {ex}")
            articles = []

        news_objects = []
        for article in articles:
            article_url = article.get("url", "")
            parsed = urlparse(article_url)
            if "finance.yahoo.com" not in parsed.netloc:
                continue

            art_date_str = article.get("seendate", "")
            if art_date_str:
                try:
                    # GDELT returns dates in "YYYYMMDDHHMMSS" format.
                    art_datetime = datetime.strptime(art_date_str, "%Y%m%d%H%M%S")
                except Exception as e:
                    print(f"Error parsing article date '{art_date_str}': {e}")
                    art_datetime = datetime.now()
            else:
                art_datetime = datetime.now()

            news_objects.append(
                News(
                    id=str(uuid.uuid4()),
                    ticker=company["ticker"],
                    date=art_datetime,
                    title=article.get("title", ""),
                    url=article_url,
                    prediction=Prediction(score=0, interpretation="No prediction", percentage_range="N/A")
                )
            )
        return news_objects
