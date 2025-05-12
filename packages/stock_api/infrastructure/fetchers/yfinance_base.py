from __future__ import annotations

import datetime as dt

import yfinance as yf
from tenacity import (
    retry,
    retry_if_exception_type,
    wait_random_exponential,
    stop_after_attempt,
)

from curl_cffi import requests as curl_requests
import requests_cache

try:
    from yfinance.exceptions import YFRateLimitError  # type: ignore
except ImportError:  # pragma: no cover

    class YFRateLimitError(Exception):
        """Fallback if the local yfinance is old."""


def _make_cached_session(expire_hours: int = 12) -> requests_cache.CachedSession:
    chrome = curl_requests.Session(impersonate="chrome")
    return requests_cache.CachedSession(
        "yahoo_cache",
        backend="sqlite",
        expire_after=dt.timedelta(hours=expire_hours),
        allowable_methods=["GET", "POST"],
        session_factory=lambda: chrome,
    )


_SESSION = _make_cached_session()


def _retryable(fn):
    return retry(
        retry=retry_if_exception_type(
            (
                YFRateLimitError,
                IOError,
                ConnectionError,
                TimeoutError,
            )
        ),
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(5),
        reraise=True,
    )(fn)


class _YFinanceBase:
    session = _SESSION

    @_retryable
    def _download(self, *args, **kwargs):  # type: ignore[override]
        kwargs["session"] = self.session
        return yf.download(*args, **kwargs)

    @_retryable
    def _ticker(self, symbol: str) -> yf.Ticker:  # type: ignore[override]
        return yf.Ticker(symbol, session=self.session)
