from __future__ import annotations

from typing import List

import pandas as pd

from stock_api.domain.historical_price import HistoricalPrice
from stock_api.domain.historical_price_fetcher import HistoricalPriceFetcher
from stock_api.infrastructure.fetchers.yfinance_base import _YFinanceBase


class YFinanceHistoricalPriceFetcher(_YFinanceBase, HistoricalPriceFetcher):
    def get_historical_prices(self, ticker: str, start, end) -> List[HistoricalPrice]:  # type: ignore[override]
        start_str, end_str = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")
        try:
            hist = self._ticker(ticker).history(start=start_str, end=end_str)
        except Exception as exc:  # pragma: no cover
            return []

        return [
            HistoricalPrice(
                date=pd.Timestamp(idx).to_pydatetime(),
                open=row["Open"],
                close=row["Close"],
            )
            for idx, row in hist.iterrows()
        ]
