from dataclasses import dataclass
from datetime import datetime, date
from typing import List
from stock_api.domain.news import News
from stock_api.domain.news_repository import NewsRepository
from stock_api.domain.prediction import Prediction


@dataclass
class GetNewsByDateCommand:
    ticker: str
    date: date


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


@dataclass
class NewsByDateList:
    ticker: str
    list: List[NewsByDate]


class GetNewsByDateCommandHandler:
    def __init__(self, repository: NewsRepository):
        self.__repository = repository

    def handle(self, command: GetNewsByDateCommand) -> NewsByDateList:
        news = News()
        prediction = Prediction()

        summaries = [
            NewsByDate(
                id=news.id,
                date=news.date,
                title=news.title,
                url=news.url,
                prediction=PredictionResponse(
                    score=prediction.score,
                    interpretation=prediction.interpretation,
                    percentage_range=prediction.percentage_range,
                ),
            )
        ]

        return NewsByDateList(command.ticker, summaries)
