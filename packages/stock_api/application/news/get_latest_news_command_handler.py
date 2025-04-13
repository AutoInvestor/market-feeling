from datetime import datetime
from dataclasses import dataclass
from stock_api.domain.news import News
from stock_api.domain.news_repository import NewsRepository
from stock_api.domain.prediction import Prediction


@dataclass
class GetLatestNewsCommand:
    ticker: str


@dataclass
class PredictionResponse:
    score: int
    interpretation: str
    percentage_range: str


@dataclass
class LatestNews:
    id: str
    ticker: str
    date: datetime
    title: str
    url: str
    prediction: PredictionResponse


class GetLatestNewsCommandHandler:
    def __init__(self, repository: NewsRepository):
        self.__repository = repository

    def handle(self, command: GetLatestNewsCommand) -> LatestNews:
        # Dummy data
        prediction = Prediction(
            score=4, interpretation="Significant rise", percentage_range="20% to 29%"
        )

        news = News(
            id="news123",
            ticker=command.ticker,
            date=datetime(2025, 4, 6, 14, 0, 0),
            title=f"Latest news for {command.ticker}",
            url="http://example.com/news",
            prediction=prediction,
        )

        prediction_response = PredictionResponse(
            score=news.prediction.score,
            interpretation=news.prediction.interpretation,
            percentage_range=news.prediction.percentage_range,
        )

        return LatestNews(
            id=news.id,
            ticker=news.ticker,
            date=news.date,
            title=news.title,
            url=news.url,
            prediction=prediction_response,
        )
