from typing import List, Optional

from stock_api.domain.company import Company
from stock_api.domain.company_repository import CompanyRepository


class InMemoryCompanyRepository(CompanyRepository):
    def __init__(self):
        self.__companies: List[Company] = [
            Company(id="AAPL", ticker="AAPL", name="Apple Inc."),
            Company(id="MSFT", ticker="MSFT", name="Microsoft Corporation"),
            Company(id="AMZN", ticker="AMZN", name="Amazon.com, Inc."),
            Company(id="GOOGL", ticker="GOOGL", name="Alphabet Inc."),
            Company(id="NVDA", ticker="NVDA", name="NVIDIA Corporation"),
            Company(id="TSLA", ticker="TSLA", name="Tesla, Inc."),
            Company(id="NFLX", ticker="NFLX", name="Netflix, Inc."),
            Company(id="ADBE", ticker="ADBE", name="Adobe Inc."),
            Company(id="INTC", ticker="INTC", name="Intel Corporation"),
        ]

    def exists(self, id: str) -> bool:
        return any(c.id == id for c in self.__companies)

    def get_all(self) -> dict[str, Company]:
        return {c.ticker: c for c in self.__companies}

    def find_by_ticker(self, ticker: str) -> Optional[Company]:
        for c in self.__companies:
            if c.ticker == ticker:
                return c
        return None

    def find_by_asset_id(self, asset_id: str) -> Optional[Company]:
        for c in self.__companies:
            if c.id == asset_id:
                return c
        return None

    def save(self, company: Company):
        for idx, stored in enumerate(self.__companies):
            if stored.ticker == company.ticker:
                self.__companies[idx] = company
                return

        self.__companies.append(company)
