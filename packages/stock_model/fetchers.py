import requests
import yfinance as yf
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from stock_model.logger import get_logger

logger = get_logger(__name__)


class YFinanceFetcher:
    """
    Fetches data from yfinance (e.g., company overview, historical prices).
    """

    @staticmethod
    def fetch_company_overview(ticker: str) -> dict:
        """
        Fetch basic company info (symbol, name, sector) using yfinance.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if info:
                return {
                    "ticker": info.get("symbol", ticker),
                    "name": info.get("longName", ""),
                    "sector": info.get("sector", "")
                }
            else:
                logger.warning(f"No company info found for {ticker}")
                return {}
        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return {}

    @staticmethod
    def fetch_historical_prices(ticker: str):
        """
        Fetch the full historical prices for a given ticker using yfinance.
        """
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="max")
            df.reset_index(inplace=True)
            df["ticker"] = ticker
            return df
        except Exception as e:
            logger.error(f"Failed fetching historical prices for {ticker}: {e}")
            return None


class YahooFinanceArticleFetcher:
    USER_AGENT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.85 Safari/537.36"
        )
    }

    @staticmethod
    def fetch_html(url: str, session: requests.Session) -> str:
        """
        Fetch the raw HTML content for a Yahoo Finance article using a shared session.
        """
        try:
            resp = session.get(url, headers=YahooFinanceArticleFetcher.USER_AGENT_HEADERS)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.RequestException:
            return ""

    @staticmethod
    def extract_text(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        article_div = soup.find("div", class_="body yf-tsvcyu")
        if article_div:
            return article_div.get_text(separator="\n", strip=True)
        return ""

class GdeltFetcher:
    """
    Fetches articles from the GDELT API specifically looking for Yahoo Finance domain mentions.
    """

    GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    def __init__(self, session: requests.Session, maxrecords=250):
        """
        Pass in a requests.Session so we can reuse connections.
        """
        self.session = session
        self.maxrecords = maxrecords
        # We'll store user agent in a single place
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/90.0.4430.85 Safari/537.36"
            )
        })

    def _build_query(self, company_name: str) -> str:
        finance_domains_block = "domain:finance.yahoo.com"
        company_block = f"\"{company_name}\""
        return f"{finance_domains_block} {company_block}"

    def fetch_news_for_company(self, company: dict, start_date: str, end_date: str) -> list:
        """
        Fetch articles for the given company in [start_date, end_date].
        This version fetches just once if your chunk logic is external –
        or you can keep your date chunk logic in here, as needed.
        """
        params = {
            "query": self._build_query(company["name"]),
            "mode": "artlist",
            "format": "json",
            "maxrecords": str(self.maxrecords),
            "startdatetime": start_date.replace("-", "") + "000000",
            "enddatetime": end_date.replace("-", "") + "235959",
            "sort": "datedesc",
        }
        try:
            response = self.session.get(self.GDELT_URL, params=params)
            if not response.text.strip():
                logger.info(f"No GDELT results for {company['name']} from {start_date} to {end_date}.")
                return []
            data = response.json()
            articles = data.get("articles", [])
            # For each article, if domain is finance.yahoo.com, fetch summary
            results = []
            for article in articles:
                article_url = article.get("url", "")
                parsed = urlparse(article_url)
                row = {
                    "ticker": company["ticker"],
                    "name": company["name"],
                    "title": article.get("title", ""),
                    "date": article.get("seendate", ""),
                    "url": article_url,
                    "summary": "",
                }
                if "finance.yahoo.com" in parsed.netloc:
                    html = YahooFinanceArticleFetcher.fetch_html(article_url, self.session)
                    row["summary"] = YahooFinanceArticleFetcher.extract_text(html)
                results.append(row)
            return results
        except Exception as ex:
            logger.warning(f"Failed to fetch articles for {company['ticker']} in {start_date}-{end_date}: {ex}")
            return []