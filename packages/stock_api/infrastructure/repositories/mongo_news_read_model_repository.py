import logging
from datetime import datetime
from pymongo import MongoClient
from stock_api.application.news.news_read_model_repository import NewsReadModelRepository
from stock_api.application.news.dtos import LatestNews, PredictionResponse

logger = logging.getLogger(__name__)

class MongoNewsReadModelRepository(NewsReadModelRepository):
    def __init__(self, uri: str | None, db_name: str):
        """
        If uri is empty or None, this repository becomes a no-op stub:
          - get() always returns None
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

    def get(self, ticker: str) -> LatestNews | None:
        if not self._enabled:
            # dummy: no data available
            return None

        doc = self._coll.find_one({"ticker": ticker.upper()})
        if not doc:
            return None
        return LatestNews(
            id=doc["id"],
            ticker=doc["ticker"],
            date=datetime.fromisoformat(doc["date"]),
            title=doc["title"],
            url=doc["url"],
            prediction=PredictionResponse(**doc["prediction"]),
        )

    def save(self, news: LatestNews) -> None:
        if not self._enabled:
            # dummy: do nothing
            return

        doc = {
            "ticker": news.ticker,
            "id": news.id,
            "date": news.date.isoformat(),
            "title": news.title,
            "url": news.url,
            "prediction": {
                "score": news.prediction.score,
                "interpretation": news.prediction.interpretation,
                "percentage_range": news.prediction.percentage_range,
            },
        }
        self._coll.update_one(
            {"ticker": news.ticker},
            {"$set": doc},
            upsert=True,
        )
