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
        company = Company(ticker=command.ticker.upper(), name="Example Corp")

        return CompanyInfoSummary(ticker=company.ticker, name=company.name)
