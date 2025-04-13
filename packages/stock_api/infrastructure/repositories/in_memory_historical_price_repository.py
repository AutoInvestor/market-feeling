from datetime import date
from typing import List, Optional
from stock_api.domain.historical_price import HistoricalPrice
from stock_api.domain.historical_price_repository import HistoricalPriceRepository


class InMemoryHistoricalPriceRepository(HistoricalPriceRepository):
    def __init__(self):
        self.data = {
            "MSFT": [HistoricalPrice(date=date(2024, 1, 2), open=350.0, close=352.5)],
            "AAPL": [HistoricalPrice(date=date(2024, 1, 2), open=150.0, close=151.0)],
        }

    def get_historical_prices(
        self, ticker: str, start: Optional[date], end: Optional[date]
    ) -> List[HistoricalPrice]:
        prices = self.data.get(ticker.upper(), [])
        if start:
            prices = [p for p in prices if p.date >= start]
        if end:
            prices = [p for p in prices if p.date <= end]
        return prices
