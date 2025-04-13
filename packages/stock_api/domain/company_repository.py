from abc import ABC, abstractmethod
from typing import Optional
from stock_api.domain.company import Company


class CompanyRepository(ABC):
    @abstractmethod
    def get_all(self) -> dict[str, Company]:
        pass

    @abstractmethod
    def get_by_ticker(self, ticker: str) -> Optional[Company]:
        pass
