from dataclasses import dataclass
from typing import List
from stock_api.domain.company_repository import CompanyRepository


@dataclass
class CompaniesTicker:
    tickers: List[str]


class GetCompaniesCommandHandler:
    def __init__(self, repository: CompanyRepository):
        self.__repository = repository

    def handle(self) -> CompaniesTicker:
        companies = self.__repository.get_all()
        tickers = [company.ticker for company in companies.values()]
        return CompaniesTicker(tickers)
