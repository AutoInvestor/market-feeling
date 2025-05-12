from dataclasses import dataclass
from datetime import date
from typing import List
from stock_api.domain.historical_price import HistoricalPrice
from stock_api.domain.historical_price_fetcher import HistoricalPriceFetcher
from stock_api.logger import get_logger

logger = get_logger(__name__)


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
    def __init__(self, fetcher: HistoricalPriceFetcher):
        self.__fetcher = fetcher

    def handle(self, command: GetCompanyHistoricalPricesCommand):
        prices = self.__fetcher.get_historical_prices(
            command.ticker, command.start, command.end
        )

        return HistoricalPricesSummary(ticker=command.ticker, prices=prices)
