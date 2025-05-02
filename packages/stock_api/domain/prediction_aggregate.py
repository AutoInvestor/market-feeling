from typing import List

from stock_api.domain.event_sourced_entity import EventSourcedEntity
from stock_api.domain.events import (
    DomainEvent,
    make_asset_feeling_detected_event,
    make_first_prediction_for_ticker_event,
)
from stock_api.domain.news import News
from stock_api.domain.prediction_state import PredictionState


class PredictionAggregate(EventSourcedEntity):
    def __init__(self, stream: List[DomainEvent]):
        self.__state = PredictionState().empty()
        super().__init__(stream)

    @staticmethod
    def empty() -> "PredictionAggregate":
        return PredictionAggregate(stream=[])

    @staticmethod
    def from_events(stream: List[DomainEvent]) -> "PredictionAggregate":
        return PredictionAggregate(stream)

    @staticmethod
    def create(ticker: str) -> "PredictionAggregate":
        prediction = PredictionAggregate.empty()
        prediction.create_first_prediction(ticker)
        return prediction

    def create_first_prediction(self, ticker):
        self.apply(make_first_prediction_for_ticker_event(ticker=ticker))

    def register_latest_news(self, news: News, score: int):
        self.apply(
            make_asset_feeling_detected_event(
                ticker=self.__state.get_aggregate_id(),
                news_id=news.id,
                url=news.url,
                title=news.title,
                date=news.date,
                score=score,
                version=self._version,
            )
        )

    def when(self, event: DomainEvent):
        event_type = event.type

        if event_type == "FIRST_TICKER_PREDICTION":
            self.__when_prediction_created(event)
        elif event_type == "ASSET_FEELING_DETECTED":
            self.__when_feeling_detected(event)
        else:
            raise ValueError("Event not defined")

    def __when_prediction_created(self, event: DomainEvent):
        if self.__state is None:
            raise ValueError("Incorrect transition from a previous state")

        self.__state = PredictionState.empty()
        self.__state = self.__state.with_prediction_created(event)

    def __when_feeling_detected(self, event: DomainEvent):
        if self.__state is None or self.__state.is_empty():
            raise ValueError("Incorrect transition from a previous state")

        self.__state = self.__state.with_feeling_detected(event)

    def get_state(self) -> PredictionState:
        return self.__state

    def filter_events_without_creation(
        self, events: List[DomainEvent]
    ) -> List[DomainEvent]:
        return [event for event in events if event.type != "FIRST_TICKER_PREDICTION"]
