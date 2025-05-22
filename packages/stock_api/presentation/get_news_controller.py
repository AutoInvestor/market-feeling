from dataclasses import dataclass
from fastapi import APIRouter, Query
from datetime import datetime
from typing import List, Optional

from stock_api.application.exceptions import BadRequestException
from stock_api.application.news.get_news_query_handler import (
    GetNewsQueryHandler,
    GetNewsQuery,
)


@dataclass
class NewsItemDTO:
    title: str
    date: datetime
    url: str
    assetId: str


class GetNewsController:
    def __init__(self, query_handler: GetNewsQueryHandler):
        self.__query_handler = query_handler
        self.__router = APIRouter()
        self.__router.add_api_route(
            "/news",
            self.handle,
            methods=["GET"],
            response_model=List[NewsItemDTO],
        )

    @property
    def router(self):
        return self.__router

    async def handle(
        self,
        asset_id: str = Query(..., alias="assetId", min_length=1),
        limit: int = Query(
            20,
            alias="limit",
            description="How many news items to return (default 20, range 1-50)",
        ),
        start_date: Optional[datetime] = Query(
            None,
            alias="startDate",
            description="ISO‑8601 start date filter (inclusive)",
        ),
        end_date: Optional[datetime] = Query(
            None,
            alias="endDate",
            description="ISO‑8601 end date filter (inclusive)",
        ),
    ) -> List[NewsItemDTO]:
        if start_date and end_date and start_date > end_date:
            raise BadRequestException(
                "startDate must be earlier than or equal to endDate"
            )

        query = GetNewsQuery(asset_id, limit, start_date, end_date)
        news_items = self.__query_handler.handle(query)

        return [
            NewsItemDTO(
                title=item.title,
                date=item.date,
                url=item.url,
                assetId=item.asset_id,
            )
            for item in news_items[:limit]
        ]
