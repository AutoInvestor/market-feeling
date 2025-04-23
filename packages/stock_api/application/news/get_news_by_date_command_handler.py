from dataclasses import dataclass
from datetime import date
from typing import List
from stock_api.domain.news_fetcher import NewsFetcher


@dataclass
class GetNewsByDateCommand:
    ticker: str
    date: date


@dataclass
class PredictionResponse:
    score: int
    interpretation: str
    percentage_range: str


@dataclass
class NewsByDate:
    id: str
    date: date
    title: str
    url: str
    prediction: PredictionResponse


@dataclass
class NewsByDateList:
    ticker: str
    list: List[NewsByDate]


class GetNewsByDateCommandHandler:
    def __init__(self, repository: NewsFetcher):
        self.__repository = repository

    def handle(self, command: GetNewsByDateCommand) -> NewsByDateList:
        return NewsByDateList(command.ticker, [])
