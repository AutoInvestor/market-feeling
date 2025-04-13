import uvicorn
from fastapi import FastAPI
from stock_api.application.companies.get_companies_command_handler import (
    GetCompaniesCommandHandler,
)
from stock_api.application.companies.get_company_historical_prices_command_handler import (
    GetCompanyHistoricalPricesCommandHandler,
)
from stock_api.application.companies.get_company_info_command_handler import (
    GetCompanyInfoCommandHandler,
)
from stock_api.application.news.get_latest_news_command_handler import (
    GetLatestNewsCommandHandler,
)
from stock_api.application.news.get_news_by_date_command_handler import (
    GetNewsByDateCommandHandler,
)
from stock_api.application.predictions.predict_from_text_command_handler import (
    PredictFromTextCommandHandler,
)
from stock_api.application.predictions.predict_from_url_command_handler import (
    PredictFromURLCommandHandler,
)
from stock_api.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
)
from stock_api.infrastructure.repositories.in_memory_historical_price_repository import (
    InMemoryHistoricalPriceRepository,
)
from stock_api.infrastructure.repositories.in_memory_news_repository import (
    InMemoryNewsRepository,
)
from stock_api.presentation.companies.get_companies_controller import (
    GetCompaniesController,
)
from stock_api.presentation.companies.get_company_historical_prices_controller import (
    GetCompanyHistoricalPricesController,
)
from stock_api.presentation.companies.get_company_info_controller import (
    GetCompanyInfoController,
)
from stock_api.presentation.news.get_latest_news_controller import (
    GetLatestNewsController,
)
from stock_api.presentation.news.get_news_by_date_controller import (
    GetNewsByDateController,
)
from stock_api.presentation.predictions.predict_from_text_controller import (
    PredictFromTextController,
)
from stock_api.presentation.predictions.predict_from_url_controller import (
    PredictFromURLController,
)

app = FastAPI()

# Composition Root Setup: instantiate repository and inject dependencies into use cases.
company_repository = InMemoryCompanyRepository()
historical_prices_repository = InMemoryHistoricalPriceRepository()
news_repository = InMemoryNewsRepository()

get_companies_command_handler = GetCompaniesCommandHandler(company_repository)
get_company_info_command_handler = GetCompanyInfoCommandHandler(company_repository)
get_historical_prices_command_handler = GetCompanyHistoricalPricesCommandHandler(
    historical_prices_repository
)
predict_from_text_command_handler = PredictFromTextCommandHandler()
predict_from_url_command_handler = PredictFromURLCommandHandler()
get_latest_news_command_handler = GetLatestNewsCommandHandler(news_repository)
get_news_by_date_command_handler = GetNewsByDateCommandHandler(news_repository)

# Instantiate controllers with their use-case dependencies.
get_companies_controller = GetCompaniesController(get_companies_command_handler)
get_company_info_controller = GetCompanyInfoController(get_company_info_command_handler)
get_company_historical_prices_controller = GetCompanyHistoricalPricesController(
    get_historical_prices_command_handler
)
prediction_text_controller = PredictFromTextController(
    predict_from_text_command_handler
)
prediction_url_controller = PredictFromURLController(predict_from_url_command_handler)
latest_news_controller = GetLatestNewsController(get_latest_news_command_handler)
news_by_date_controller = GetNewsByDateController(get_news_by_date_command_handler)

# Include each controller's router into the FastAPI app.
app.include_router(get_companies_controller.router)
app.include_router(get_company_info_controller.router)
app.include_router(get_company_historical_prices_controller.router)
app.include_router(prediction_text_controller.router)
app.include_router(prediction_url_controller.router)
app.include_router(latest_news_controller.router)
app.include_router(news_by_date_controller.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
