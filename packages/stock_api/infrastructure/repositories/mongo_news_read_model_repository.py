from datetime import datetime, date, time
from typing import List

from pymongo import MongoClient, ASCENDING, DESCENDING

from stock_api.application.news.latest_news_dto import LatestNews
from stock_api.application.news.news_read_model_repository import (
    NewsReadModelRepository,
)
from stock_api.logger import get_logger

logger = get_logger(__name__)


class MongoNewsReadModelRepository(NewsReadModelRepository):
    def __init__(self, uri: str | None, db_name: str):
        """
        If uri is empty or None, this repository becomes a no-op stub:
          - get() always returns empty
          - save() does nothing
        """
        self._enabled = bool(uri)
        if not self._enabled:
            logger.warning(
                "No MONGODB_URI provided: MongoNewsReadModelRepository disabled, using dummy behavior."
            )
            return

        client = MongoClient(uri)
        self._coll = client[db_name]["news"]

    def get(self, news_id: str) -> LatestNews | None:
        if not self._enabled:
            # dummy: no data available
            return None

        doc = self._coll.find_one({"_id": news_id})
        if not doc:
            return None
        return LatestNews(
            id=doc["_id"],
            ticker=doc["ticker"],
            date=datetime.fromisoformat(doc["date"]),
            title=doc["title"],
            url=doc["url"],
            feeling=doc["feeling"],
        )

    def save(self, news: LatestNews) -> None:
        if not self._enabled:
            # dummy: do nothing
            return

        doc = {
            "_id": news.id,
            "ticker": news.ticker,
            "date": news.date.isoformat(),
            "title": news.title,
            "url": news.url,
            "feeling": news.feeling,
        }
        self._coll.update_one(
            {"_id": news.id},
            {"$set": doc},
            upsert=True,
        )

    def get_by_date_range(
        self, ticker: str, start_date: date, end_date: date
    ) -> List[LatestNews]:
        if not self._enabled:
            return []

        start_iso = datetime.combine(start_date, time.min).isoformat()
        end_iso = datetime.combine(end_date, time.max).isoformat()

        cursor = self._coll.find(
            {
                "ticker": ticker,
                "date": {"$gte": start_iso, "$lte": end_iso},
            }
        ).sort("date", ASCENDING)

        results: List[LatestNews] = []
        for doc in cursor:
            results.append(
                LatestNews(
                    id=doc["_id"],
                    ticker=doc["ticker"],
                    date=datetime.fromisoformat(doc["date"]),
                    title=doc["title"],
                    url=doc["url"],
                    feeling=doc["feeling"],
                )
            )

        return results

    def get_latest_news_for_ticker(self, ticker: str, limit: int) -> List[LatestNews]:
        if not self._enabled:
            return []

        if limit < 1:
            return []
        limit = min(limit, 50)

        cursor = (
            self._coll.find({"ticker": ticker})
            .sort("date", DESCENDING)  # newest → oldest
            .limit(limit)
        )

        results: List[LatestNews] = []
        for doc in cursor:
            results.append(
                LatestNews(
                    id=doc["_id"],
                    ticker=doc["ticker"],
                    date=datetime.fromisoformat(doc["date"]),
                    title=doc["title"],
                    url=doc["url"],
                    feeling=doc["feeling"],
                )
            )

        return results
