from dataclasses import dataclass
from fastapi import APIRouter, Depends
from datetime import date
from typing import List
from stock_api.application.companies.get_company_historical_prices_command_handler import (
    GetCompanyHistoricalPricesCommandHandler,
    GetCompanyHistoricalPricesCommand,
)


@dataclass
class PriceDTO:
    date: date
    open: float
    close: float


@dataclass
class GetCompanyHistoricalPricesResponseDTO:
    ticker: str
    historical_prices: List[PriceDTO]


@dataclass
class GetCompanyHistoricalPricesQueryDTO:
    start: date
    end: date


class GetCompanyHistoricalPricesController:
    def __init__(self, command_handler: GetCompanyHistoricalPricesCommandHandler):
        self.__command_handler = command_handler
        self.__router = APIRouter()
        self.__router.add_api_route(
            "/companies/{ticker}/historical-prices",
            self.handle,
            methods=["GET"],
            response_model=GetCompanyHistoricalPricesResponseDTO,
        )

    @property
    def router(self):
        return self.__router

    async def handle(
        self, ticker: str, query: GetCompanyHistoricalPricesQueryDTO = Depends()
    ) -> GetCompanyHistoricalPricesResponseDTO:
        command = GetCompanyHistoricalPricesCommand(ticker, query.start, query.end)
        response = self.__command_handler.handle(command)
        price_dtos = [
            PriceDTO(date=p.date, open=p.open, close=p.close) for p in response.prices
        ]
        return GetCompanyHistoricalPricesResponseDTO(
            ticker=ticker, historical_prices=price_dtos
        )
