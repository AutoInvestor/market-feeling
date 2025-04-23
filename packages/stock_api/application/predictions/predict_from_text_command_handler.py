from dataclasses import dataclass

from stock_api.application.exceptions import NotFoundException
from stock_api.domain.company_repository import CompanyRepository
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
    def __init__(self, repository: CompanyRepository, model: PredictionModel):
        self.__repository = repository
        self.__model = model

    def handle(self, command: PredictFromTextCommand) -> PredictionScore:
        logger.info("PredictFromText for ticker=%s", command.ticker)

        company = self.__repository.get_by_ticker(command.ticker)

        if company is None:
            logger.warning("Company not found: %s", command.ticker)
            raise NotFoundException(f"Company '{command.ticker}' not found")

        # 1) get raw score from model
        raw_score: RawScore = self.__model.get_prediction_from_text(
            command.news_text, company.name
        )
        logger.debug("Raw score: %d", raw_score.value)

        # 2) delegate interpretation + range to domain’s PredictionState
        state = PredictionState()
        state.apply_score(raw_score.value)

        # 3) build and return the DTO
        result = PredictionScore(
            ticker=command.ticker,
            score=state.score,
            interpretation=state.interpretation,
            percentage_range=state.percentage_range,
        )
        logger.info(
            "PredictFromText result for %s → score=%d, interp=%s",
            command.ticker, state.score, state.interpretation
        )
        return result
