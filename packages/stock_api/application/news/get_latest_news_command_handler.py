from stock_api.application.exceptions import NotFoundException
from stock_api.application.news.dtos import GetLatestNewsCommand, LatestNews, PredictionResponse
from stock_api.domain.company_repository import CompanyRepository
from stock_api.domain.news_repository import NewsRepository
from stock_api.domain.prediction_model import PredictionModel
from stock_api.domain.event_store_repository import EventStoreRepository
from stock_api.application.news.latest_news_read_model_repository import LatestNewsReadModelRepository
from stock_api.domain.event_publisher import DomainEventPublisher
from stock_api.domain.prediction_aggregate import PredictionAggregate
from stock_api.domain.prediction_state import PredictionState
from stock_api.domain.raw_score import RawScore


class GetLatestNewsCommandHandler:
    def __init__(
        self,
        news_repository: NewsRepository,
        company_repository: CompanyRepository,
        model: PredictionModel,
        event_store: EventStoreRepository,
        read_model: LatestNewsReadModelRepository,
        publisher: DomainEventPublisher,
    ):
        self.__news_repository = news_repository
        self.__company_repository = company_repository
        self.__model = model
        self.__event_store = event_store
        self.__read_model = read_model
        self.__publisher = publisher

    def handle(self, command: GetLatestNewsCommand) -> LatestNews:
        # 1) Validate company exists
        company = self.__company_repository.get_by_ticker(command.ticker)
        if company is None:
            raise NotFoundException(f"Company '{command.ticker}' not found")

        # 2) Try read model
        existing = self.__read_model.get(command.ticker)
        if existing:
            return existing

        # 3) Fetch raw news
        news = self.__news_repository.get_latest_news(command.ticker)
        if news is None:
            raise NotFoundException(f"No news found for '{command.ticker}'")

        # 4) Get only a RawScore VO:
        raw_score: RawScore = self.__model.get_prediction_from_url(
            news.url, company.name
        )

        # 5) Build DTO
        temp = PredictionState()
        temp.apply_score(raw_score.value)

        pred_resp = PredictionResponse(
            score=temp.score,
            interpretation=temp.interpretation,
            percentage_range=temp.percentage_range,
        )
        latest_news = LatestNews(
            id=news.id, ticker=news.ticker, date=news.date,
            title=news.title, url=news.url, prediction=pred_resp,
        )

        # 6) Event‐sourcing: feed the pure integer into the aggregate
        past = self.__event_store.get_events(latest_news.id)
        agg  = PredictionAggregate.detect(
            latest_news, past, raw_score.value
        )

        # 7) persist & publish
        for evt in agg.get_uncommitted_events():
            self.__event_store.append(evt)
            self.__publisher.publish(evt)
        agg.mark_events_as_committed()

        # 8) update read model
        self.__read_model.save(latest_news)

        return latest_news
