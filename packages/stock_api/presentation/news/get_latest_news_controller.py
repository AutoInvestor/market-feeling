from dataclasses import dataclass
from fastapi import APIRouter
from datetime import datetime
from stock_api.application.news.get_latest_news_command_handler import (
    GetLatestNewsCommandHandler,
    GetLatestNewsCommand,
)


@dataclass
class GetLatestNewsResponseDTO:
    id: str
    ticker: str
    date: datetime
    title: str
    url: str
    feeling: int


class GetLatestNewsController:
    def __init__(self, command_handler: GetLatestNewsCommandHandler):
        self.__command_handler = command_handler
        self.__router = APIRouter()
        self.__router.add_api_route(
            "/companies/{ticker}/news/latest",
            self.handle,
            methods=["GET"],
            response_model=GetLatestNewsResponseDTO,
        )

    @property
    def router(self):
        return self.__router

    async def handle(self, ticker: str) -> GetLatestNewsResponseDTO:
        command = GetLatestNewsCommand(ticker)
        latest_news = self.__command_handler.handle(command)
        return GetLatestNewsResponseDTO(
            id=latest_news.id,
            ticker=ticker,
            date=latest_news.date,
            title=latest_news.title,
            url=latest_news.url,
            feeling=latest_news.feeling,
        )
