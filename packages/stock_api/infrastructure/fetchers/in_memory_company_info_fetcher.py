from typing import Dict, Optional

from stock_api.domain.company import Company
from stock_api.domain.company_info_fetcher import CompanyInfoFetcher


class InMemoryCompanyInfoFetcher(CompanyInfoFetcher):
    _companies: Dict[str, Company] = {
        "AAPL": Company(id="AAPL", ticker="AAPL", name="Apple Inc."),
        "MSFT": Company(id="MSFT", ticker="MSFT", name="Microsoft Corporation"),
        "AMZN": Company(id="AMZN", ticker="AMZN", name="Amazon.com, Inc."),
        "GOOGL": Company(id="GOOGL", ticker="GOOGL", name="Alphabet Inc."),
        "NVDA": Company(id="NVDA", ticker="NVDA", name="NVIDIA Corporation"),
        "TSLA": Company(id="TSLA", ticker="TSLA", name="Tesla, Inc."),
        "NFLX": Company(id="NFLX", ticker="NFLX", name="Netflix, Inc."),
        "ADBE": Company(id="ADBE", ticker="ADBE", name="Adobe Inc."),
        "INTC": Company(id="INTC", ticker="INTC", name="Intel Corporation"),
    }

    def get_info(self, ticker: str) -> Optional[Company]:
        return self._companies.get(ticker.upper())
