from __future__ import annotations

from typing import Optional

from stock_api.domain.company_info import CompanyInfo
from stock_api.domain.company_info_fetcher import CompanyInfoFetcher
from stock_api.infrastructure.fetchers.yfinance_base import _YFinanceBase


class YFinanceCompanyInfoFetcher(_YFinanceBase, CompanyInfoFetcher):
    def get_info(self, ticker: str) -> Optional[CompanyInfo]:  # type: ignore[override]
        try:
            info = self._ticker(ticker).info
        except Exception as exc:  # pragma: no cover
            return None

        return CompanyInfo(
            name=info.get("longName") or info.get("shortName") or ticker.upper()
        )
