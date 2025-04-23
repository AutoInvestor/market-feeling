from dataclasses import dataclass
from typing import List
from stock_api.domain.company_repository import CompanyRepository
from stock_api.logger import get_logger

logger = get_logger(__name__)

@dataclass
class CompaniesTicker:
    tickers: List[str]


class GetCompaniesCommandHandler:
    def __init__(self, repository: CompanyRepository):
        self.__repository = repository

    def handle(self) -> CompaniesTicker:
        logger.info("Fetching all company tickers")

        companies = self.__repository.get_all()
        tickers = [company.ticker for company in companies.values()]

        logger.debug("Found %d companies", len(tickers))

        return CompaniesTicker(tickers)
