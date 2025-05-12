from abc import ABC, abstractmethod
from typing import Optional
from stock_api.domain.company_info import CompanyInfo


class CompanyInfoFetcher(ABC):
    @abstractmethod
    def get_info(self, ticker: str) -> Optional[CompanyInfo]:
        pass
