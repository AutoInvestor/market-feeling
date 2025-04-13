from dataclasses import dataclass
from fastapi import APIRouter
from typing import List
from stock_api.application.companies.get_companies_command_handler import (
    GetCompaniesCommandHandler,
)


@dataclass
class GetCompaniesResponseDTO:
    companies: List[str]


class GetCompaniesController:
    def __init__(self, command_handler: GetCompaniesCommandHandler):
        self.__command_handler = command_handler
        self.__router = APIRouter()
        self.__router.add_api_route(
            "/companies",
            self.handle,
            methods=["GET"],
            response_model=GetCompaniesResponseDTO,
        )

    @property
    def router(self):
        return self.__router

    async def handle(self) -> GetCompaniesResponseDTO:
        companies_ticker = self.__command_handler.handle()
        return GetCompaniesResponseDTO(companies=companies_ticker.tickers)
