from datetime import date
from typing import List, Dict

from stock_api.domain.historical_price import HistoricalPrice
from stock_api.domain.historical_price_fetcher import HistoricalPriceFetcher


class InMemoryHistoricalPriceFetcher(HistoricalPriceFetcher):
    def __init__(self):
        self.__prices: Dict[str, List[HistoricalPrice]] = {
            "AAPL": [
                HistoricalPrice(date=date(2024, 1, 1), open=130.0, close=132.5),
                HistoricalPrice(date=date(2024, 1, 2), open=132.5, close=135.0),
            ],
            "MSFT": [
                HistoricalPrice(date=date(2024, 1, 1), open=220.0, close=225.0),
            ],
        }

    def get_historical_prices(self, ticker: str, start, end) -> List[HistoricalPrice]:
        all_prices = self.__prices.get(ticker.upper(), [])
        return [p for p in all_prices if start <= p.date <= end]
