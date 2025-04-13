from dataclasses import dataclass
from fastapi import APIRouter
from stock_api.application.predictions.predict_from_text_command_handler import (
    PredictFromTextCommandHandler,
    PredictFromTextCommand,
)


@dataclass
class PredictionTextRequestDTO:
    ticker: str
    news_text: str


@dataclass
class PredictionDTO:
    score: int
    interpretation: str
    percentage_range: str


@dataclass
class PredictionResponseDTO:
    ticker: str
    prediction: PredictionDTO


class PredictFromTextController:
    def __init__(self, command_handler: PredictFromTextCommandHandler):
        self.__command_handler = command_handler
        self.__router = APIRouter()
        self.__router.add_api_route(
            "/prediction/text",
            self.handle,
            methods=["POST"],
            response_model=PredictionResponseDTO,
        )

    @property
    def router(self):
        return self.__router

    async def handle(self, request: PredictionTextRequestDTO) -> PredictionResponseDTO:
        command = PredictFromTextCommand(request.ticker, request.news_text)
        prediction = self.__command_handler.handle(command)
        prediction_dto = PredictionDTO(
            score=prediction.score,
            interpretation=prediction.interpretation,
            percentage_range=prediction.percentage_range,
        )
        return PredictionResponseDTO(ticker=request.ticker, prediction=prediction_dto)
