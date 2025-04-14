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
        news = self.__repository.get_latest_news(command.ticker)
        if news is None:
            news = News(
                id="",
                ticker=command.ticker.upper(),
                date=datetime.now(),
                title="No news found",
                url="",
                prediction=Prediction(score=0, interpretation="No prediction", percentage_range="N/A")
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
