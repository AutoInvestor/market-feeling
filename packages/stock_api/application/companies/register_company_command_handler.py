from dataclasses import dataclass

from stock_api.application.exceptions import NotFoundException
from stock_api.domain.company import Company
from stock_api.domain.company_info_fetcher import CompanyInfoFetcher
from stock_api.domain.company_repository import CompanyRepository
from stock_api.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RegisterCompanyCommand:
    id: str
    ticker: str


class RegisterCompanyCommandHandler:
    def __init__(self, fetcher: CompanyInfoFetcher, repository: CompanyRepository):
        self.__fetcher = fetcher
        self.__repository = repository

    def handle(self, command: RegisterCompanyCommand):
        company_info = self.__fetcher.get_info(command.ticker)
        if company_info is None:
            raise NotFoundException(
                f"Company '{command.ticker}' not found in yahoo finance"
            )

        if self.__repository.exists(command.id):
            return

        company = Company(command.id, command.ticker, company_info.name)
        self.__repository.save(company)
