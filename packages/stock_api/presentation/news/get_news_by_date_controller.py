from dataclasses import dataclass
from fastapi import APIRouter, Depends
from datetime import date
from typing import List

from stock_api.application.news.get_news_by_date_command_handler import (
    GetNewsByDateCommandHandler,
    GetNewsByDateCommand,
)


@dataclass
class PredictionDTO:
    score: int
    interpretation: str
    percentage_range: str


@dataclass
class NewsItemDTO:
    id: str
    date: date
    title: str
    url: str
    prediction: PredictionDTO


@dataclass
class NewsByDateResponseDTO:
    ticker: str
    date: date
    news: List[NewsItemDTO]


@dataclass
class GetNewsByDateQueryDTO:
    date: date


class GetNewsByDateController:
    def __init__(self, command_handler: GetNewsByDateCommandHandler):
        self.__command_handler = command_handler
        self.__router = APIRouter()
        self.__router.add_api_route(
            "/companies/{ticker}/news",
            self.handle,
            methods=["GET"],
            response_model=NewsByDateResponseDTO,
        )

    @property
    def router(self):
        return self.__router

    async def handle(
        self, ticker: str, query: GetNewsByDateQueryDTO = Depends()
    ) -> NewsByDateResponseDTO:
        command = GetNewsByDateCommand(ticker, query.date)
        news_items = self.__command_handler.handle(command)
        news_dtos = []
        for item in news_items.list:
            news_dtos.append(
                NewsItemDTO(
                    id=item.id,
                    date=item.date,
                    title=item.title,
                    url=item.url,
                    prediction=PredictionDTO(
                        score=item.prediction.score,
                        interpretation=item.prediction.interpretation,
                        percentage_range=item.prediction.percentage_range,
                    ),
                )
            )
        return NewsByDateResponseDTO(ticker=ticker, date=query.date, news=news_dtos)
