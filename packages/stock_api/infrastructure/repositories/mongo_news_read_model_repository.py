from datetime import datetime
from pymongo import MongoClient
from stock_api.application.news.news_read_model_repository import (
    NewsReadModelRepository,
)
from stock_api.application.news.dtos import LatestNews, PredictionResponse


class MongoNewsReadModelRepository(NewsReadModelRepository):
    def __init__(self, uri: str, db_name: str):
        client = MongoClient(uri)
        self._coll = client[db_name]["news"]

    def get(self, ticker: str) -> LatestNews | None:
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
