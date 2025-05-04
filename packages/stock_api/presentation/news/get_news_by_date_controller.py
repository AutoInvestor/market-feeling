from dataclasses import dataclass
from fastapi import APIRouter, Depends
from datetime import date
from typing import List

from stock_api.application.exceptions import BadRequestException
from stock_api.application.news.get_news_by_date_query_handler import (
    GetNewsByDateQueryHandler,
    GetNewsByDateQuery,
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
class GetNewsByDateQueryDTO:
    start_date: date
    end_date: date


class GetNewsByDateController:
    def __init__(self, query_handler: GetNewsByDateQueryHandler):
        self.__query_handler = query_handler
        self.__router = APIRouter()
        self.__router.add_api_route(
            "/companies/{ticker}/news",
            self.handle,
            methods=["GET"],
            response_model=List[NewsItemDTO],
        )

    @property
    def router(self):
        return self.__router

    async def handle(
        self, ticker: str, query: GetNewsByDateQueryDTO = Depends()
    ) -> List[NewsItemDTO]:
        if query.start_date > query.end_date:
            raise BadRequestException("start_date must be on or before end_date")

        query = GetNewsByDateQuery(ticker, query.start_date, query.end_date)

        news_items = self.__query_handler.handle(query)

        news_dtos = []
        for item in news_items:
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
        return news_dtos
