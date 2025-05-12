import yfinance as yf
from typing import Optional, Dict
from stock_api.domain.company import Company
from stock_api.domain.company_info_fetcher import CompanyInfoFetcher


class YFinanceCompanyInfoFetcher(CompanyInfoFetcher):
    def get_info(self, ticker: str) -> Optional[Company]:
        stock = yf.Ticker(ticker)
        info = stock.info
        name = info.get("longName") or info.get("shortName") or ticker
        return Company(ticker=ticker, name=name)
