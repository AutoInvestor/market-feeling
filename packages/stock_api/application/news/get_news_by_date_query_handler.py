from dataclasses import dataclass
from datetime import date
from typing import List

from stock_api.application.news.dtos import LatestNews
from stock_api.application.news.news_read_model_repository import (
    NewsReadModelRepository,
)
from stock_api.domain.news_fetcher import NewsFetcher


@dataclass
class GetNewsByDateQuery:
    ticker: str
    start_date: date
    end_date: date


@dataclass
class PredictionResponse:
    score: int
    interpretation: str
    percentage_range: str


@dataclass
class NewsByDate:
    id: str
    date: date
    title: str
    url: str
    prediction: PredictionResponse


class GetNewsByDateQueryHandler:
    def __init__(self, read_model: NewsReadModelRepository):
        self.__read_model = read_model

    def handle(self, query: GetNewsByDateQuery) -> List[NewsByDate]:
        items: List[LatestNews] = self.__read_model.get_by_date_range(
            query.ticker, query.start_date, query.end_date
        )

        if not items:
            return []

        return [
            NewsByDate(
                id=i.id,
                date=i.date,
                title=i.title,
                url=i.url,
                prediction=PredictionResponse(
                    score=i.prediction.score,
                    interpretation=i.prediction.interpretation,
                    percentage_range=i.prediction.percentage_range,
                ),
            )
            for i in items
        ]
