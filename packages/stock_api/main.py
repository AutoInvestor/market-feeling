import uvicorn
from fastapi import FastAPI

from stock_api.application.companies.register_company_command_handler import (
    RegisterCompanyCommandHandler,
)
from stock_api.application.news.get_news_query_handler import GetNewsQueryHandler
from stock_api.config import settings
from stock_api.logger import get_logger
from stock_api.infrastructure.http_exception_handler import HttpExceptionHandler

from stock_api.application.news.register_news_command_handler import (
    RegisterNewsCommandHandler,
)
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
from stock_api.infrastructure.listeners.companies.pubsub_companies_event_subscriber import (
    PubSubCompaniesEventSubscriber,
)
from stock_api.infrastructure.listeners.news.pubsub_news_event_subscriber import (
    PubSubNewsEventSubscriber,
)

# Presentation
from stock_api.presentation.get_news_controller import GetNewsController

app = FastAPI()
logger = get_logger(__name__)
logger.info("Starting up in %s mode", settings.ENVIRONMENT)

HttpExceptionHandler(app)

prediction_model = JoblibPredictionModel("models/stock_model.joblib")

if settings.ENVIRONMENT.lower() == "testing":
    event_store = InMemoryEventStoreRepository()
    read_model = InMemoryNewsReadModelRepository()
    publisher = InMemoryDomainEventPublisher()
    company_repo = InMemoryCompanyRepository()
else:
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
get_news_handler = GetNewsQueryHandler(read_model, company_repo)

# Presentation controllers
app.include_router(GetNewsController(get_news_handler).router)

# Pub/Sub subscriber wiring (only in production)
if settings.ENVIRONMENT.lower() != "testing":
    company_register_handler = RegisterCompanyCommandHandler(company_repo)
    companies_subscriber = PubSubCompaniesEventSubscriber(
        command_handler=company_register_handler,
        project_id=settings.GCP_PROJECT,
        subscription=settings.PUBSUB_SUBSCRIPTION_CORE,
    )
    news_register_handler = RegisterNewsCommandHandler(
        company_repo, prediction_model, event_store, read_model, publisher
    )
    news_subscriber = PubSubNewsEventSubscriber(
        command_handler=news_register_handler,
        project_id=settings.GCP_PROJECT,
        subscription=settings.PUBSUB_SUBSCRIPTION_NEWS_SCRAPER,
    )

    @app.on_event("startup")
    def start_subscriber():
        companies_subscriber.listen()
        news_subscriber.listen()

    @app.on_event("shutdown")
    def stop_subscriber():
        companies_subscriber.stop()
        news_subscriber.stop()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, access_log=False, log_level="critical")
