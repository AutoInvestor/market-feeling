from typing import List
import pandas as pd
import yfinance as yf
from stock_api.domain.historical_price import HistoricalPrice
from stock_api.domain.historical_price_repository import HistoricalPriceRepository

class YFinanceHistoricalPriceRepository(HistoricalPriceRepository):
    def get_historical_prices(self, ticker: str, start, end) -> List[HistoricalPrice]:
        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_str, end=end_str)
        prices = []
        for index, row in hist.iterrows():
            dt = pd.Timestamp(index).to_pydatetime()
            prices.append(HistoricalPrice(date=dt, open=row["Open"], close=row["Close"]))
        return prices
