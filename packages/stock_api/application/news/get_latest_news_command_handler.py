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
        publisher: DomainEventPublisher,
    ):
        self.__news_repository = news_repository
        self.__company_repository = company_repository
        self.__model = model
        self.__event_store = event_store
        self.__read_model = read_model
        self.__publisher = publisher

    def handle(self, command: GetLatestNewsCommand) -> LatestNews:
        logger.info("GetLatestNews for ticker='%s'", command.ticker)

        # 1) Validate company exists
        company = self.__company_repository.get_by_ticker(command.ticker)
        if company is None:
            logger.warning("Company not found: %s", command.ticker)
            return LatestNews(
                id="",
                ticker=command.ticker,
                date=datetime.min,
                title="",
                url="",
                prediction=PredictionResponse(
                    score=0,
                    interpretation="",
                    percentage_range="",
                ),
            )

        # 2) Try read model
        existing = self.__read_model.get(command.ticker)
        if existing:
            logger.debug("Read-model cache hit for %s", command.ticker)
            return existing

        # 3) Fetch raw news
        news = self.__news_repository.get_latest_news(command.ticker)
        if news is None:
            logger.warning("No news found for %s", command.ticker)
            raise NotFoundException(f"No news found for '{command.ticker}'")

        # 4) Get only a RawScore VO
        raw_score: RawScore = self.__model.get_prediction_from_url(
            news.url, company.name
        )
        logger.info(
            "Predicted raw score=%d for news id=%s",
            raw_score.value,
            news.id,
        )

        # 5) Build in‐memory state
        temp = PredictionState()
        temp.apply_score(raw_score.value)

        # 6) Event‐sourcing: rehydrate & detect
        past = self.__event_store.get_events(news.id)

        agg = PredictionAggregate.detect(news, past, raw_score.value)
        expected_version = len(past)

        # 7) persist & publish with optimistic concurrency
        uncommitted = agg.get_uncommitted_events()
        try:
            for evt in uncommitted:
                self.__event_store.append(
                    aggregate_id=news.id,
                    events=[evt],
                    expected_version=expected_version,
                )
                self.__publisher.publish(evt)
                expected_version += 1
        except ConcurrencyError:
            logger.info(
                "Concurrency conflict on news.id=%s: another pod already wrote; skipping",
                news.id,
            )
            return self.__read_model.get(command.ticker)

        agg.mark_events_as_committed()

        # 8) update read model
        pred_resp = PredictionResponse(
            score=temp.score,
            interpretation=temp.interpretation,
            percentage_range=temp.percentage_range,
        )
        latest_news = LatestNews(
            id=news.id,
            ticker=news.ticker,
            date=news.date,
            title=news.title,
            url=news.url,
            prediction=pred_resp,
        )
        self.__read_model.save(latest_news)

        logger.info("Completed GetLatestNews for %s", command.ticker)
        return latest_news
