from typing import Optional
from stock_api.domain.company import Company
from stock_api.domain.company_repository import CompanyRepository


class InMemoryCompanyRepository(CompanyRepository):
    def __init__(self):
        self._companies = {
            "AAPL": Company(ticker="AAPL", name="Apple Inc."),
            "MSFT": Company(ticker="MSFT", name="Microsoft Corporation"),
            "GOOG": Company(ticker="GOOG", name="Alphabet Inc."),
            "AMZN": Company(ticker="AMZN", name="Amazon.com Inc."),
            "NFLX": Company(ticker="NFLX", name="Netflix Inc."),
        }

    def get_all(self) -> dict[str, Company]:
        return self._companies

    def get_by_ticker(self, ticker: str) -> Optional[Company]:
        return self._companies.get(ticker.upper())
