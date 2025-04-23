from datetime import datetime
from dataclasses import dataclass

from stock_api.application.exceptions import NotFoundException
from stock_api.domain.company_repository import CompanyRepository
from stock_api.domain.news import News
from stock_api.domain.news_repository import NewsRepository
from stock_api.domain.prediction import Prediction
from stock_api.domain.prediction_model import PredictionModel


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
    def __init__(
        self,
        news_repository: NewsRepository,
        company_repository: CompanyRepository,
        model: PredictionModel,
    ):
        self.__news_repository = news_repository
        self.__company_repository = company_repository
        self.__model = model

    def handle(self, command: GetLatestNewsCommand) -> LatestNews:
        company = self.__company_repository.get_by_ticker(command.ticker)

        if company is None:
            raise NotFoundException(f"Company '{command.ticker}' not found")

        news = self.__news_repository.get_latest_news(command.ticker)

        if news is None:
            news = News()
            prediction = Prediction()

            prediction_response = PredictionResponse(
                prediction.score, prediction.interpretation, prediction.percentage_range
            )

            return LatestNews(
                id=news.id,
                ticker=news.ticker,
                date=news.date,
                title=news.title,
                url=news.url,
                prediction=prediction_response,
            )

        company_name = company.name
        prediction = self.__model.get_prediction_from_url(news.url, company_name)

        prediction_response = PredictionResponse(
            score=prediction.score,
            interpretation=prediction.interpretation,
            percentage_range=prediction.percentage_range,
        )

        return LatestNews(
            id=news.id,
            ticker=news.ticker,
            date=news.date,
            title=news.title,
            url=news.url,
            prediction=prediction_response,
        )
