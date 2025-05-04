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
class PredictionResponseDTO:
    feeling: int


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
        feeling = self.__command_handler.handle(command)
        return PredictionResponseDTO(feeling=feeling)
