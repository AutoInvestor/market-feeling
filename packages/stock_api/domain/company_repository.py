from abc import ABC, abstractmethod
from typing import Optional

from stock_api.domain.company import Company


class CompanyRepository(ABC):
    @abstractmethod
    def exists(self, id: str) -> bool:
        pass

    @abstractmethod
    def get_all(self) -> dict[str, Company]:
        pass

    @abstractmethod
    def find_by_ticker(self, ticker: str) -> Optional[Company]:
        pass

    @abstractmethod
    def find_by_asset_id(self, asset_id: str) -> Optional[Company]:
        pass

    @abstractmethod
    def save(self, company: Company):
        pass
