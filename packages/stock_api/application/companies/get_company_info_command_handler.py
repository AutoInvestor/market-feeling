from dataclasses import dataclass
from stock_api.domain.company import Company
from stock_api.domain.company_repository import CompanyRepository


@dataclass
class GetCompanyInfoCommand:
    ticker: str


@dataclass
class CompanyInfoSummary:
    ticker: str
    name: str


class GetCompanyInfoCommandHandler:
    def __init__(self, repository: CompanyRepository):
        self.__repository = repository

    def handle(self, command: GetCompanyInfoCommand) -> CompanyInfoSummary:
        company_info = self.__repository.get_by_ticker(command.ticker)
        company = Company(ticker=command.ticker, name=company_info.name)
        return CompanyInfoSummary(ticker=company.ticker, name=company.name)
