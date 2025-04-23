from dataclasses import dataclass

from stock_api.application.exceptions import NotFoundException
from stock_api.domain.company_repository import CompanyRepository
from stock_api.domain.prediction_model import PredictionModel


@dataclass
class PredictFromTextCommand:
    ticker: str
    news_text: str


@dataclass
class PredictionScore:
    ticker: str
    score: int
    interpretation: str
    percentage_range: str


class PredictFromTextCommandHandler:
    def __init__(self, repository: CompanyRepository, model: PredictionModel):
        self.__repository = repository
        self.__model = model

    def handle(self, command: PredictFromTextCommand) -> PredictionScore:
        company = self.__repository.get_by_ticker(command.ticker)

        if company is None:
            raise NotFoundException(f"Company '{command.ticker}' not found")

        company_name = company.name
        prediction = self.__model.get_prediction_from_text(
            command.news_text, company_name
        )

        return PredictionScore(
            ticker=command.ticker,
            score=prediction.score,
            interpretation=prediction.interpretation,
            percentage_range=prediction.percentage_range,
        )
