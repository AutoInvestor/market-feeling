import datetime
from dataclasses import dataclass

from stock_api.application.exceptions import NotFoundException
from stock_api.application.news.latest_news_dto import LatestNews
from stock_api.domain.company_repository import CompanyRepository
from stock_api.domain.news import News
from stock_api.domain.prediction_model import PredictionModel
from stock_api.domain.event_store_repository import EventStoreRepository
from stock_api.application.news.news_read_model_repository import (
    NewsReadModelRepository,
)
from stock_api.domain.event_publisher import DomainEventPublisher
from stock_api.domain.raw_feeling import RawFeeling
from stock_api.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RegisterNewsCommand:
    id: str
    ticker: str
    date: datetime
    title: str
    url: str


class RegisterNewsCommandHandler:
    def __init__(
        self,
        company_repository: CompanyRepository,
        model: PredictionModel,
        event_store: EventStoreRepository,
        read_model: NewsReadModelRepository,
        event_publisher: DomainEventPublisher,
    ):
        self.__company_repository = company_repository
        self.__model = model
        self.__event_store = event_store
        self.__read_model = read_model
        self.__event_publisher = event_publisher

    def handle(self, command: RegisterNewsCommand):
        logger.info("GetLatestNews for ticker='%s'", command.ticker)

        # Validate company exists
        company = self.__company_repository.find_by_ticker(command.ticker)
        if company is None:
            raise NotFoundException(f"Company '{command.ticker}' not found")

        # Create news from the command DTO
        news = News(
            command.id, command.ticker, command.date, command.title, command.url
        )

        # Try read model
        existing = self.__read_model.get(news.id)
        if existing:
            logger.debug("Read-model cache hit for %s", command.ticker)
            return existing

        # Get a feeling for the latest news
        raw_feeling: RawFeeling = self.__model.get_prediction_from_url(
            news.url, company.name
        )

        # Get the last prediction for this ticker, if exists
        prediction = self.__event_store.find_by_id(command.ticker)

        # Register the latest news in the prediction aggregate
        prediction.register_latest_news(news, raw_feeling.value)

        # Save the events into the write-side event store
        events = prediction.get_uncommitted_events()

        # Persist events into the event store
        self.__event_store.save(prediction)

        # Publish events to notify subscribers
        self.__event_publisher.publish(events)

        # After publishing, clear the uncommitted events from the aggregate
        prediction.mark_events_as_committed()

        # Transform the prediction to a VO
        state = prediction.get_state()
        latest_news = LatestNews(
            id=news.id,
            ticker=news.ticker,
            date=news.date,
            title=news.title,
            url=news.url,
            feeling=state.feeling,
        )

        # Update read-model
        self.__read_model.save(latest_news)

        logger.info("Completed GetLatestNews for %s", command.ticker)
