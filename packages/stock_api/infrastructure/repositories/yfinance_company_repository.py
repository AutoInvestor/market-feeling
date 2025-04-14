import yfinance as yf
from typing import Optional, Dict
from stock_api.domain.company import Company
from stock_api.domain.company_repository import CompanyRepository


class YFinanceCompanyRepository(CompanyRepository):
    def __init__(self):
        self.__tickers = [
            "AAPL",  # Apple Inc.
            "MSFT",  # Microsoft Corporation
            "AMZN",  # Amazon.com, Inc.
            "GOOGL",  # Alphabet Inc.
            "FB",  # Meta Platforms, Inc.
            "NVDA",  # NVIDIA Corporation
            "TSLA",  # Tesla, Inc.
            "NFLX",  # Netflix, Inc.
            "ADBE",  # Adobe Inc.
            "INTC",  # Intel Corporation
        ]

    def get_all(self) -> Dict[str, Company]:
        companies = {}
        for ticker in self.__tickers:
            stock = yf.Ticker(ticker)
            info = stock.info
            name = info.get("longName") or info.get("shortName") or ticker
            companies[ticker.upper()] = Company(ticker=ticker.upper(), name=name)
        return companies

    def get_by_ticker(self, ticker: str) -> Optional[Company]:
        ticker_upper = ticker.upper()

        if ticker_upper not in [t.upper() for t in self.__tickers]:
            return None

        stock = yf.Ticker(ticker_upper)
        info = stock.info
        name = info.get("longName") or info.get("shortName") or ticker_upper
        return Company(ticker=ticker_upper, name=name)
