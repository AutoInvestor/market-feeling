from dataclasses import dataclass
from fastapi import APIRouter
from stock_api.application.companies.get_company_info_command_handler import (
    GetCompanyInfoCommandHandler,
    GetCompanyInfoCommand,
)


@dataclass
class GetCompanyInfoResponseDTO:
    ticker: str
    name: str


class GetCompanyInfoController:
    def __init__(self, command_handler: GetCompanyInfoCommandHandler):
        self.__command_handler = command_handler
        self.__router = APIRouter()
        self.__router.add_api_route(
            "/companies/{ticker}",
            self.handle,
            methods=["GET"],
            response_model=GetCompanyInfoResponseDTO,
        )

    @property
    def router(self):
        return self.__router

    async def handle(self, ticker: str) -> GetCompanyInfoResponseDTO:
        command = GetCompanyInfoCommand(ticker)
        company = self.__command_handler.handle(command)
        return GetCompanyInfoResponseDTO(ticker=company.ticker, name=company.name)
