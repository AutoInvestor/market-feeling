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
    def __init__(self, fetcher: CompanyInfoFetcher):
        self.__fetcher = fetcher

    def handle(self, command: GetCompanyInfoCommand) -> CompanyInfoSummary:
        company_info = self.__fetcher.get_info(command.ticker)

        if company_info is None:
            raise NotFoundException(f"Company '{command.ticker}' not found")

        return CompanyInfoSummary(ticker=command.ticker, name=company_info.name)
