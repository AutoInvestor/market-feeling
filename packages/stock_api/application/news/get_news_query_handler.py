from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from stock_api.application.exceptions import NotFoundException
from stock_api.application.news.latest_news_dto import LatestNews
from stock_api.application.news.news_read_model_repository import (
    NewsReadModelRepository,
)
from stock_api.domain.company_repository import CompanyRepository


@dataclass
class GetNewsQuery:
    asset_id: str
    limit: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]


@dataclass
class NewsItem:
    title: str
    date: datetime
    url: str
    asset_id: str


class GetNewsQueryHandler:
    def __init__(
        self, read_model: NewsReadModelRepository, company_repository: CompanyRepository
    ):
        self.__read_model = read_model
        self.__company_repository = company_repository

    def handle(self, query: GetNewsQuery) -> List[NewsItem]:
        company = self.__company_repository.find_by_asset_id(query.asset_id)
        if company is None:
            raise NotFoundException(
                f"Company with assetId '{query.asset_id}' not found"
            )

        ticker: str = company.ticker

        latest_news: List[LatestNews]
        if query.start_date is not None or query.end_date is not None:
            latest_news: List[LatestNews] = self.__read_model.get_by_date_range(
                ticker=ticker,
                start_date=query.start_date.date(),
                end_date=query.end_date.date(),
            )
        else:
            limit = max(1, min(query.limit, 50))
            latest_news: List[LatestNews] = (
                self.__read_model.get_latest_news_for_ticker(ticker, limit)
            )

        if not latest_news:
            return []

        latest_news.sort(key=lambda n: n.date, reverse=True)

        return [
            NewsItem(
                title=item.title,
                date=item.date,
                url=item.url,
                asset_id=query.asset_id,
            )
            for item in latest_news
        ]
