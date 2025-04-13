from dataclasses import dataclass
from fastapi import APIRouter
from stock_api.application.predictions.predict_from_url_command_handler import (
    PredictFromURLCommandHandler,
    PredictFromURLCommand,
)


@dataclass
class PredictionUrlRequestDTO:
    ticker: str
    url: str


@dataclass
class PredictionDTO:
    score: int
    interpretation: str
    percentage_range: str


@dataclass
class PredictionResponseDTO:
    ticker: str
    prediction: PredictionDTO


class PredictFromURLController:
    def __init__(self, command_handler: PredictFromURLCommandHandler):
        self.__command_handler = command_handler
        self.__router = APIRouter()
        self.__router.add_api_route(
            "/prediction/url",
            self.handle,
            methods=["POST"],
            response_model=PredictionResponseDTO,
        )

    @property
    def router(self):
        return self.__router

    async def handle(self, request: PredictionUrlRequestDTO) -> PredictionResponseDTO:
        command = PredictFromURLCommand(request.ticker, request.url)
        prediction = self.__command_handler.handle(command)
        prediction_dto = PredictionDTO(
            score=prediction.score,
            interpretation=prediction.interpretation,
            percentage_range=prediction.percentage_range,
        )
        return PredictionResponseDTO(
            ticker=request.ticker.upper(), prediction=prediction_dto
        )
