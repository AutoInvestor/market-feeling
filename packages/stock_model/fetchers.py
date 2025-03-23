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
    """
    Utility to fetch and parse Yahoo Finance article HTML.
    """

    USER_AGENT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.85 Safari/537.36"
        )
    }

    @staticmethod
    def fetch_html(url: str) -> str:
        """
        Fetch the raw HTML content for a Yahoo Finance article.
        """
        try:
            response = requests.get(url, headers=YahooFinanceArticleFetcher.USER_AGENT_HEADERS)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch article HTML from {url}: {e}")
            return ""

    @staticmethod
    def extract_text(html: str) -> str:
        """
        Extract the main body text from the fetched article HTML.
        """
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
    USER_AGENT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/90.0.4430.85 Safari/537.36"
        )
    }

    def __init__(self, timespan="3m", maxrecords=250):
        """
        :param timespan: e.g., '3m' for 3 months
        :param maxrecords: number of max articles per query
        """
        self.timespan = timespan
        self.maxrecords = maxrecords

    def _build_query(self, company_name: str) -> str:
        """
        Build a GDELT query that targets Yahoo Finance articles for the given company name.
        """
        finance_domains_block = "domain:finance.yahoo.com"
        company_block = f"\"{company_name}\""
        return f"{finance_domains_block} {company_block}"

    def fetch_news_for_company(self, company: dict) -> list:
        """
        Fetch GDELT news articles for the specified company.
        Return a list of dictionaries for each article.
        """
        query = self._build_query(company["name"])
        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "maxrecords": str(self.maxrecords),
            "timespan": self.timespan,
            "sort": "datedesc",
        }

        results = []
        try:
            response = requests.get(self.GDELT_URL, params=params, headers=self.USER_AGENT_HEADERS)
            if not response.text.strip():
                logger.info(f"Empty GDELT response for {company['name']} ({company['ticker']}).")
                return results

            data = response.json()
            articles = data.get("articles", [])

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

                # Fetch the article text if from Yahoo Finance
                if "finance.yahoo.com" in parsed.netloc:
                    html = YahooFinanceArticleFetcher.fetch_html(article_url)
                    row["summary"] = YahooFinanceArticleFetcher.extract_text(html)

                results.append(row)

        except Exception as e:
            logger.warning(f"Error fetching news for {company['name']} ({company['ticker']}): {e}")

        return results
