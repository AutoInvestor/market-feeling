from dataclasses import dataclass
from datetime import datetime, date
from typing import List
from stock_api.domain.historical_price import HistoricalPrice
from stock_api.domain.historical_price_repository import HistoricalPriceRepository


@dataclass
class GetCompanyHistoricalPricesCommand:
    ticker: str
    start: date
    end: date


@dataclass
class HistoricalPricesSummary:
    ticker: str
    prices: List[HistoricalPrice]


class GetCompanyHistoricalPricesCommandHandler:
    def __init__(self, repository: HistoricalPriceRepository):
        self.__repository = repository

    def handle(self, command: GetCompanyHistoricalPricesCommand):
        prices = [
            HistoricalPrice(date=datetime(2025, 4, 6), open=100.0, close=105.0),
            HistoricalPrice(date=datetime(2025, 4, 7), open=106.0, close=104.0),
        ]
        return HistoricalPricesSummary(ticker=command.ticker, prices=prices)
