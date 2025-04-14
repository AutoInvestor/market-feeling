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
        domain_news = self.__repository.get_news_by_date(command.ticker, command.date)

        summaries = [
            NewsByDate(
                id=n.id,
                date=n.date.date(),
                title=n.title,
                url=n.url,
                prediction=PredictionResponse(
                    score=n.prediction.score,
                    interpretation=n.prediction.interpretation,
                    percentage_range=n.prediction.percentage_range,
                ),
            )
            for n in domain_news
        ]

        return NewsByDateList(ticker=command.ticker.upper(), list=summaries)
