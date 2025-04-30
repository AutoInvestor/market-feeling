from datetime import datetime
from stock_api.application.exceptions import NotFoundException
from stock_api.application.news.dtos import (
    GetLatestNewsCommand,
    LatestNews,
    PredictionResponse,
)
from stock_api.domain.company_info_fetcher import CompanyInfoFetcher
from stock_api.domain.news_fetcher import NewsFetcher
from stock_api.domain.prediction_model import PredictionModel
from stock_api.domain.event_store_repository import EventStoreRepository
from stock_api.domain.exceptions import ConcurrencyError
from stock_api.application.news.news_read_model_repository import (
    NewsReadModelRepository,
)
from stock_api.domain.event_publisher import DomainEventPublisher
from stock_api.domain.prediction_aggregate import PredictionAggregate
from stock_api.domain.prediction_state import PredictionState
from stock_api.domain.raw_score import RawScore
from stock_api.logger import get_logger

logger = get_logger(__name__)


class GetLatestNewsCommandHandler:
    def __init__(
        self,
        news_repository: NewsFetcher,
        company_repository: CompanyInfoFetcher,
        model: PredictionModel,
        event_store: EventStoreRepository,
        read_model: NewsReadModelRepository,
        event_publisher: DomainEventPublisher,
    ):
        self.__news_repository = news_repository
        self.__company_repository = company_repository
        self.__model = model
        self.__event_store = event_store
        self.__read_model = read_model
        self.__event_publisher = event_publisher

    def handle(self, command: GetLatestNewsCommand) -> LatestNews:
        logger.info("GetLatestNews for ticker='%s'", command.ticker)

        # Validate company exists
        company = self.__company_repository.get_by_ticker(command.ticker)
        if company is None:
            logger.warning("Company not found: %s", command.ticker)
            raise NotFoundException(f"Company '{command.ticker}' not found")

        # Fetch raw news
        news = self.__news_repository.get_latest_news(command.ticker)
        if news is None:
            logger.warning("No news found for %s", command.ticker)
            return LatestNews.empty()

        # Try read model - best effort
        existing = self.__read_model.get(command.ticker)
        if existing:
            logger.debug("Read-model cache hit for %s", command.ticker)
            return existing

        # Get a score for the latest news
        raw_score: RawScore = self.__model.get_prediction_from_url(
            news.url, company.name
        )

        # Get the last prediction for this ticker, if exists
        prediction = self.__event_store.find_by_id(command.ticker)

        # Update the state of the aggregate
        if not prediction:
            prediction = PredictionAggregate.create(command.ticker)

        prediction.register_latest_news(news, raw_score.value)

        # Save the events into the write-side event store
        events = prediction.get_uncommitted_events()

        # Persist events into the event store
        self.__event_store.save(prediction)

        # Publish events to notify subscribers
        self.__event_publisher.publish(events)

        # After publishing, clear the uncommitted events from the aggregate
        prediction.mark_events_as_committed()

        # Transform the prediction to a VO
        pred_resp = PredictionResponse(
            score=raw_score.value,
            interpretation="",
            percentage_range="",
        )
        latest_news = LatestNews(
            id=news.id,
            ticker=news.ticker,
            date=news.date,
            title=news.title,
            url=news.url,
            prediction=pred_resp,
        )

        # Update read-model
        self.__read_model.save(latest_news)

        logger.info("Completed GetLatestNews for %s", command.ticker)
        return latest_news
