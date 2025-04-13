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
        # Dummy data
        prediction = Prediction(
            score=4, interpretation="Significant rise", percentage_range="20% to 29%"
        )

        domain_news = [
            News(
                id="news123",
                ticker=command.ticker,
                date=datetime(2025, 4, 6, 14, 0, 0),
                title=f"News A for {command.ticker}",
                url="http://example.com/news-a",
                prediction=prediction,
            ),
            News(
                id="news124",
                ticker=command.ticker,
                date=datetime(2025, 4, 6, 16, 30, 0),
                title=f"News B for {command.ticker}",
                url="http://example.com/news-b",
                prediction=prediction,
            ),
        ]

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

        return NewsByDateList(ticker=command.ticker, list=summaries)
