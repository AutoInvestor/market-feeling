from dataclasses import dataclass

from stock_api.domain.company import Company
from stock_api.domain.company_repository import CompanyRepository
from stock_api.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RegisterCompanyCommand:
    id: str
    ticker: str
    name: str


class RegisterCompanyCommandHandler:
    def __init__(self, repository: CompanyRepository):
        self.__repository = repository

    def handle(self, command: RegisterCompanyCommand):
        if self.__repository.exists(command.id):
            return

        company = Company(command.id, command.ticker, command.name)
        self.__repository.save(company)
