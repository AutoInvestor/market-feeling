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
from stock_api.application.news.get_news_by_date_command_handler import (
    GetNewsByDateCommandHandler,
)
from stock_api.application.predictions.predict_from_text_command_handler import (
    PredictFromTextCommandHandler,
)
from stock_api.application.predictions.predict_from_url_command_handler import (
    PredictFromURLCommandHandler,
)
from stock_api.config import settings
from stock_api.infrastructure.fetchers.yfinance_company_info_fetcher import (
    YFinanceCompanyInfoFetcher,
)
from stock_api.infrastructure.fetchers.yfinance_historical_price_fetcher import (
    YFinanceHistoricalPriceFetcher,
)
from stock_api.infrastructure.fetchers.yfinance_news_fetcher import YFinanceNewsFetcher
from stock_api.infrastructure.http_exception_handler import HttpExceptionHandler
from stock_api.infrastructure.joblib_prediction_model import JoblibPredictionModel
from stock_api.infrastructure.publishers.pubsub_event_publisher import (
    PubSubEventPublisher,
)
from stock_api.infrastructure.repositories.in_memory_event_store_repository import (
    InMemoryEventStoreRepository,
)
from stock_api.infrastructure.repositories.in_memory_news_read_model_repository import (
    InMemoryNewsReadModelRepository,
)
from stock_api.infrastructure.publishers.in_memory_domain_event_publisher import (
    InMemoryDomainEventPublisher,
)
from stock_api.infrastructure.repositories.mongo_event_store_repository import (
    MongoEventStoreRepository,
)
from stock_api.application.news.get_latest_news_command_handler import (
    GetLatestNewsCommandHandler,
)
from stock_api.infrastructure.repositories.mongo_news_read_model_repository import (
    MongoNewsReadModelRepository,
)
from stock_api.logger import get_logger
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

logger = get_logger(__name__)
logger.info("Starting up in %s mode", settings.ENVIRONMENT)

# Exceptions Handler.
HttpExceptionHandler(app)

# Common Infra.
company_repository = YFinanceCompanyInfoFetcher()
historical_prices_repository = YFinanceHistoricalPriceFetcher()
news_repository = YFinanceNewsFetcher()
prediction_model = JoblibPredictionModel("models/stock_model.joblib")

if settings.ENVIRONMENT.lower() == "testing":
    event_store = InMemoryEventStoreRepository()
    read_model = InMemoryNewsReadModelRepository()
    publisher = InMemoryDomainEventPublisher()
    logger.info("Using in-memory adapters for testing")
else:
    event_store = MongoEventStoreRepository(
        settings.MONGODB_URI.get_secret_value(), settings.MONGODB_DB
    )
    read_model = MongoNewsReadModelRepository(
        settings.MONGODB_URI.get_secret_value(), settings.MONGODB_DB
    )
    publisher = PubSubEventPublisher(settings.GCP_PROJECT, settings.PUBSUB_TOPIC)
    logger.info("Using MongoDB Atlas + Pub/Sub adapters for production")

# Commands
get_companies_command_handler = GetCompaniesCommandHandler(company_repository)
get_company_info_command_handler = GetCompanyInfoCommandHandler(company_repository)
get_historical_prices_command_handler = GetCompanyHistoricalPricesCommandHandler(
    historical_prices_repository
)
predict_from_text_command_handler = PredictFromTextCommandHandler(
    company_repository, prediction_model
)
predict_from_url_command_handler = PredictFromURLCommandHandler(
    company_repository, prediction_model
)
get_latest_news_command_handler = GetLatestNewsCommandHandler(
    news_repository,
    company_repository,
    prediction_model,
    event_store,
    read_model,
    publisher,
)
get_news_by_date_command_handler = GetNewsByDateCommandHandler(news_repository)

# Controllers.
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
    uvicorn.run(app, host="0.0.0.0", port=8080, access_log=False, log_level="critical")
