import re
import requests
import time
import random
from urllib.parse import urlparse
from datetime import datetime, timedelta
from stock_model.logger import get_logger

logger = get_logger(__name__)

# GDELT DOC 2.0 API endpoint and limits
URL = "https://api.gdeltproject.org/api/v2/doc/doc"
MAX_SPAN = timedelta(days=90)  # Maximum window size allowed by GDELT
MIN_INTERVAL = 5  # Minimum seconds between requests per GDELT policy

# Default headers to mimic a real browser
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
}


class GdeltFetcher:
    def __init__(self, session: requests.Session | None = None, maxrecords: int = 250):
        # Use provided session or create a new one
        self.session = session or requests.Session()
        # Apply headers to mimic a browser
        self.session.headers.update(DEFAULT_HEADERS)
        self.maxrecords = maxrecords

    def _windows(self, start: datetime, end: datetime):
        """
        Yield (start, end) tuples each spanning at most MAX_SPAN.
        """
        current = start
        while current < end:
            nxt = min(current + MAX_SPAN, end)
            yield current, nxt
            current = nxt + timedelta(seconds=1)

    def _gdelt_get(self, params: dict, max_retries: int = 5) -> requests.Response:
        """
        Perform a GDELT API GET, retrying on rate limits and network timeouts.
        """
        wait = MIN_INTERVAL
        last_exc = None

        for attempt in range(1, max_retries + 1):
            try:
                resp = self.session.get(URL, params=params, timeout=10)
                # If not rate-limited, return
                if resp.status_code != 429:
                    return resp
                # else, log and back off
                logger.warning(
                    "GDELT 429 – retrying in %.1fs (attempt %d/%d)",
                    wait,
                    attempt,
                    max_retries,
                )
            except requests.exceptions.RequestException as e:
                last_exc = e
                logger.warning(
                    "GDELT request exception: %s – retrying in %.1fs (attempt %d/%d)",
                    e,
                    wait,
                    attempt,
                    max_retries,
                )
            # Sleep with jitter before retrying
            jitter = random.uniform(0, 1)
            time.sleep(wait + jitter)
            wait *= 2

        # All retries exhausted
        if last_exc:
            # Propagate the last exception
            raise last_exc
        return resp

    def fetch_news_for_company(self, company: dict, start: str, end: str) -> list[dict]:
        """
        Fetch news articles for a given company between ISO dates `start` and `end`.

        Returns a list of dicts with keys: id, ticker, date, title, url.
        """
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        results: list[dict] = []

        for w_start, w_end in self._windows(start_dt, end_dt):
            params = {
                "query": f'domain:finance.yahoo.com "{company.get("name")}"',
                "mode": "artlist",
                "format": "json",
                "maxrecords": str(self.maxrecords),
                "startdatetime": w_start.strftime("%Y%m%d%H%M%S"),
                "enddatetime": w_end.strftime("%Y%m%d%H%M%S"),
                "sort": "datedesc",
            }

            try:
                resp = self._gdelt_get(params)
            except Exception as e:
                logger.warning("GDELT fetch window failed: %s", e)
                continue

            if not resp.ok:
                logger.warning("GDELT HTTP %s – %s", resp.status_code, resp.text[:200])
            elif "application/json" not in resp.headers.get("Content-Type", ""):
                logger.warning("GDELT non-JSON response: %.200s", resp.text)
            else:
                articles = resp.json().get("articles", [])
                for art in articles:
                    url = art.get("url", "")
                    if "finance.yahoo.com" not in urlparse(url).netloc:
                        continue

                    seen_date = art.get("seendate", "")
                    clean = re.sub(r"\D", "", seen_date)
                    try:
                        dt = datetime.strptime(clean, "%Y%m%d%H%M%S")
                    except ValueError:
                        logger.warning("error in parsing date '%s'", seen_date)
                        dt = datetime.utcnow()

                    results.append(
                        {
                            "ticker": company.get("ticker"),
                            "date": dt.strftime("%Y-%m-%dT%H:%M:%S"),
                            "title": art.get("title", ""),
                            "url": url,
                        }
                    )

            # Respect the API rate limit between windows
            time.sleep(MIN_INTERVAL)

        return results
