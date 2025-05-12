import uvicorn
from fastapi import FastAPI

from stock_api.application.companies.register_company_command_handler import (
    RegisterCompanyCommandHandler,
)
from stock_api.config import settings
from stock_api.infrastructure.fetchers.in_memory_company_info_fetcher import (
    InMemoryCompanyInfoFetcher,
)
from stock_api.infrastructure.fetchers.in_memory_historical_price_fetcher import (
    InMemoryHistoricalPriceFetcher,
)
from stock_api.infrastructure.fetchers.in_memory_news_fetcher import InMemoryNewsFetcher
from stock_api.logger import get_logger
from stock_api.infrastructure.http_exception_handler import HttpExceptionHandler

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
from stock_api.application.news.get_news_by_date_query_handler import (
    GetNewsByDateQueryHandler,
)
from stock_api.application.predictions.predict_from_text_command_handler import (
    PredictFromTextCommandHandler,
)
from stock_api.application.predictions.predict_from_url_command_handler import (
    PredictFromURLCommandHandler,
)

from stock_api.infrastructure.fetchers.yfinance_company_info_fetcher import (
    YFinanceCompanyInfoFetcher,
)
from stock_api.infrastructure.fetchers.yfinance_historical_price_fetcher import (
    YFinanceHistoricalPriceFetcher,
)
from stock_api.infrastructure.fetchers.yfinance_news_fetcher import YFinanceNewsFetcher

from stock_api.infrastructure.joblib_prediction_model import JoblibPredictionModel

from stock_api.infrastructure.repositories.in_memory_company_repository import (
    InMemoryCompanyRepository,
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
from stock_api.infrastructure.repositories.mongo_company_repository import (
    MongoCompanyRepository,
)
from stock_api.infrastructure.repositories.mongo_event_store_repository import (
    MongoEventStoreRepository,
)
from stock_api.infrastructure.repositories.mongo_news_read_model_repository import (
    MongoNewsReadModelRepository,
)
from stock_api.infrastructure.publishers.pubsub_event_publisher import (
    PubSubEventPublisher,
)
from stock_api.infrastructure.listeners.pubsub_event_subscriber import (
    PubSubEventSubscriber,
)

# Presentation
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

HttpExceptionHandler(app)

prediction_model = JoblibPredictionModel("models/stock_model.joblib")

if settings.ENVIRONMENT.lower() == "testing":
    company_fetcher = InMemoryCompanyInfoFetcher()
    historical_prices_repo = InMemoryHistoricalPriceFetcher()
    news_repo = InMemoryNewsFetcher()

    event_store = InMemoryEventStoreRepository()
    read_model = InMemoryNewsReadModelRepository()
    publisher = InMemoryDomainEventPublisher()
    company_repo = InMemoryCompanyRepository()
else:
    company_fetcher = YFinanceCompanyInfoFetcher()
    historical_prices_repo = YFinanceHistoricalPriceFetcher()
    news_repo = YFinanceNewsFetcher()

    event_store = MongoEventStoreRepository(
        settings.MONGODB_URI.get_secret_value(), settings.MONGODB_DB
    )
    read_model = MongoNewsReadModelRepository(
        settings.MONGODB_URI.get_secret_value(), settings.MONGODB_DB
    )
    publisher = PubSubEventPublisher(settings.GCP_PROJECT, settings.PUBSUB_TOPIC)
    company_repo = MongoCompanyRepository(
        settings.MONGODB_URI.get_secret_value(), settings.MONGODB_DB
    )

# Application command handlers
get_companies_handler = GetCompaniesCommandHandler(company_repo)
get_company_info_handler = GetCompanyInfoCommandHandler(company_fetcher)
get_historical_prices_handler = GetCompanyHistoricalPricesCommandHandler(
    historical_prices_repo
)
predict_text_handler = PredictFromTextCommandHandler(company_repo, prediction_model)
predict_url_handler = PredictFromURLCommandHandler(company_repo, prediction_model)
get_latest_news_handler = GetLatestNewsCommandHandler(
    news_repo, company_repo, prediction_model, event_store, read_model, publisher
)
get_news_by_date_handler = GetNewsByDateQueryHandler(read_model)

# Presentation controllers
app.include_router(GetCompaniesController(get_companies_handler).router)
app.include_router(GetCompanyInfoController(get_company_info_handler).router)
app.include_router(
    GetCompanyHistoricalPricesController(get_historical_prices_handler).router
)
app.include_router(PredictFromTextController(predict_text_handler).router)
app.include_router(PredictFromURLController(predict_url_handler).router)
app.include_router(GetLatestNewsController(get_latest_news_handler).router)
app.include_router(GetNewsByDateController(get_news_by_date_handler).router)

# Pub/Sub subscriber wiring (only in production)
if settings.ENVIRONMENT.lower() != "testing":
    register_handler = RegisterCompanyCommandHandler(company_fetcher, company_repo)
    subscriber = PubSubEventSubscriber(
        command_handler=register_handler,
        project_id=settings.GCP_PROJECT,
        subscription=settings.PUBSUB_SUBSCRIPTION_CORE,
    )

    @app.on_event("startup")
    def start_subscriber():
        subscriber.listen()

    @app.on_event("shutdown")
    def stop_subscriber():
        subscriber.stop()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, access_log=False, log_level="critical")
