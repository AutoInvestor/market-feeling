from dataclasses import dataclass
from fastapi import APIRouter
from stock_api.application.predictions.predict_from_text_command_handler import (
    PredictFromTextCommandHandler,
    PredictFromTextCommand,
)


@dataclass
class PredictionTextRequestDTO:
    ticker: str
    text: str


@dataclass
class PredictionResponseDTO:
    feeling: int


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
        command = PredictFromTextCommand(request.ticker, request.text)
        feeling = self.__command_handler.handle(command)
        return PredictionResponseDTO(feeling=feeling)
