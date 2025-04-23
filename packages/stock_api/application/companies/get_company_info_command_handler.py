from dataclasses import dataclass

from stock_api.application.exceptions import NotFoundException
from stock_api.domain.company import Company
from stock_api.domain.company_info_fetcher import CompanyInfoFetcher
from stock_api.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GetCompanyInfoCommand:
    ticker: str


@dataclass
class CompanyInfoSummary:
    ticker: str
    name: str


class GetCompanyInfoCommandHandler:
    def __init__(self, repository: CompanyInfoFetcher):
        self.__repository = repository

    def handle(self, command: GetCompanyInfoCommand) -> CompanyInfoSummary:
        logger.info("Looking up company info for ticker='%s'", command.ticker)

        company_info = self.__repository.get_by_ticker(command.ticker)

        if company_info is None:
            logger.warning("Company not found: %s", command.ticker)
            raise NotFoundException(f"Company '{command.ticker}' not found")

        logger.debug("Found company: %s", company_info.name)

        company = Company(ticker=command.ticker, name=company_info.name)
        return CompanyInfoSummary(ticker=company.ticker, name=company.name)
