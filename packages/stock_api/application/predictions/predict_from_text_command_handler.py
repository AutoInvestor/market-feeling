from dataclasses import dataclass

from stock_api.application.exceptions import NotFoundException
from stock_api.domain.company_info_fetcher import CompanyInfoFetcher
from stock_api.domain.prediction_model import PredictionModel
from stock_api.domain.prediction_state import PredictionState
from stock_api.domain.raw_score import RawScore
from stock_api.logger import get_logger

logger = get_logger(__name__)


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
    def __init__(self, repository: CompanyInfoFetcher, model: PredictionModel):
        self.__repository = repository
        self.__model = model

    def handle(self, command: PredictFromTextCommand) -> PredictionScore:
        company = self.__repository.get_by_ticker(command.ticker)

        if company is None:
            raise NotFoundException(f"Company '{command.ticker}' not found")

        # 1) get raw score from model
        raw_score: RawScore = self.__model.get_prediction_from_text(
            command.news_text, company.name
        )

        # 2) delegate interpretation + range to domain’s PredictionState
        interpretation = PredictionState().get_interpretation_from_score(
            raw_score.value
        )
        percentage_range = PredictionState().get_range_from_score(raw_score.value)

        # 3) build and return the DTO
        result = PredictionScore(
            ticker=command.ticker,
            score=raw_score.value,
            interpretation=interpretation,
            percentage_range=percentage_range,
        )
        return result
