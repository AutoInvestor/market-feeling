from abc import ABC, abstractmethod
from datetime import date
from typing import List
from stock_api.domain.historical_price import HistoricalPrice


class HistoricalPriceRepository(ABC):
    @abstractmethod
    def get_historical_prices(
        self, ticker: str, start: date, end: date
    ) -> List[HistoricalPrice]:
        pass
