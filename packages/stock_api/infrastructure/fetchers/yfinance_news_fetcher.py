from __future__ import annotations

import uuid
from datetime import datetime, date
from typing import List, Optional

from stock_api.domain.news import News
from stock_api.domain.news_fetcher import NewsFetcher
from stock_api.infrastructure.fetchers.yfinance_base import _YFinanceBase


class YFinanceNewsFetcher(_YFinanceBase, NewsFetcher):
    @staticmethod
    def _make_deterministic_id(
        ticker: str, pub_dt: datetime, title: str, url: str
    ) -> str:
        raw = "||".join(
            [
                ticker.upper().strip(),
                pub_dt.isoformat(),
                title.strip(),
                url.strip(),
            ]
        )
        return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))

    def _fetch_news_objects(self, ticker_upper: str) -> List[News]:
        try:
            items = self._ticker(ticker_upper).news or []  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover
            return []

        results: List[News] = []
        for item in items:
            ts = item.get("providerPublishTime") or item.get("providerPublishTimeMs")
            if ts is None:
                # Legacy fallback: explore *content.pubDate*
                try:
                    content = item.get("content", {})
                    ts = datetime.strptime(
                        content.get("pubDate", ""), "%Y-%m-%dT%H:%M:%SZ"
                    ).timestamp()
                except Exception:
                    continue

            pub_dt = datetime.utcfromtimestamp(int(ts))
            title = item.get("title") or item.get("content", {}).get("title", "")
            url = item.get("link") or item.get("url") or item.get("previewUrl")
            if not url:
                url = item.get("canonicalUrl", {}).get("url", "")

            if not title or not url:
                continue

            results.append(
                News(
                    id=self._make_deterministic_id(ticker_upper, pub_dt, title, url),
                    ticker=ticker_upper,
                    date=pub_dt,
                    title=title,
                    url=url,
                )
            )
        return results

    def get_latest_news(self, ticker: str) -> Optional[News]:  # type: ignore[override]
        ticker_upper = ticker.upper()
        news_items = self._fetch_news_objects(ticker_upper)
        return max(news_items, key=lambda n: n.date) if news_items else None

    def get_news_by_date(self, ticker: str, news_date: date) -> List[News]:  # type: ignore[override]
        ticker_upper = ticker.upper()
        news_items = self._fetch_news_objects(ticker_upper)
        return [n for n in news_items if n.date.date() == news_date]
