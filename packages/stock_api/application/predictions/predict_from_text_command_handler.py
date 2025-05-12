from dataclasses import dataclass

from stock_api.application.exceptions import NotFoundException
from stock_api.domain.company_repository import CompanyRepository
from stock_api.domain.prediction_model import PredictionModel
from stock_api.domain.raw_feeling import RawFeeling
from stock_api.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PredictFromTextCommand:
    ticker: str
    news_text: str


class PredictFromTextCommandHandler:
    def __init__(self, repository: CompanyRepository, model: PredictionModel):
        self.__repository = repository
        self.__model = model

    def handle(self, command: PredictFromTextCommand) -> int:
        company = self.__repository.find_by_ticker(command.ticker)

        if company is None:
            raise NotFoundException(f"Company '{command.ticker}' not found")

        raw_feeling: RawFeeling = self.__model.get_prediction_from_text(
            command.news_text, company.name
        )

        return raw_feeling.value
