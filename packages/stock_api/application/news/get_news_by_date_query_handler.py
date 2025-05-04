from dataclasses import dataclass
from datetime import date
from typing import List

from stock_api.application.news.latest_news_dto import LatestNews
from stock_api.application.news.news_read_model_repository import (
    NewsReadModelRepository,
)


@dataclass
class GetNewsByDateQuery:
    ticker: str
    start_date: date
    end_date: date


@dataclass
class NewsByDate:
    id: str
    date: date
    title: str
    url: str
    feeling: int


class GetNewsByDateQueryHandler:
    def __init__(self, read_model: NewsReadModelRepository):
        self.__read_model = read_model

    def handle(self, query: GetNewsByDateQuery) -> List[NewsByDate]:
        items: List[LatestNews] = self.__read_model.get_by_date_range(
            query.ticker, query.start_date, query.end_date
        )

        if not items:
            return []

        return [
            NewsByDate(
                id=i.id,
                date=i.date,
                title=i.title,
                url=i.url,
                feeling=i.feeling,
            )
            for i in items
        ]
