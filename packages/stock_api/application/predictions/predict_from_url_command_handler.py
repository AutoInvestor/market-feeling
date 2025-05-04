from dataclasses import dataclass

from stock_api.application.exceptions import NotFoundException
from stock_api.domain.company_info_fetcher import CompanyInfoFetcher
from stock_api.domain.prediction_model import PredictionModel
from stock_api.domain.raw_feeling import RawFeeling
from stock_api.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PredictFromURLCommand:
    ticker: str
    url: str


class PredictFromURLCommandHandler:
    def __init__(self, repository: CompanyInfoFetcher, model: PredictionModel):
        self.__repository = repository
        self.__model = model

    def handle(self, command: PredictFromURLCommand) -> int:
        company = self.__repository.get_by_ticker(command.ticker)

        if company is None:
            raise NotFoundException(f"Company '{command.ticker}' not found")

        raw_feeling: RawFeeling = self.__model.get_prediction_from_url(
            command.url, company.name
        )

        return raw_feeling.value
