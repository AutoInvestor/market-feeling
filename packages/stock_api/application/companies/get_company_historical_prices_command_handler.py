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
    def __init__(self, repository: HistoricalPriceFetcher):
        self.__repository = repository

    def handle(self, command: GetCompanyHistoricalPricesCommand):
        logger.info(
            "Fetching historical prices for %s between %s and %s",
            command.ticker,
            command.start,
            command.end,
        )

        prices = self.__repository.get_historical_prices(
            command.ticker, command.start, command.end
        )

        logger.debug("Received %d price points", len(prices))

        return HistoricalPricesSummary(ticker=command.ticker, prices=prices)
