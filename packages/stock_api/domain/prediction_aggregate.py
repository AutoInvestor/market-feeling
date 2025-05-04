from typing import List

from stock_api.domain.event_sourced_entity import EventSourcedEntity
from stock_api.domain.events import (
    DomainEvent,
    make_asset_feeling_detected_event,
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

    def register_latest_news(self, news: News, feeling: int):
        self.apply(
            make_asset_feeling_detected_event(
                ticker=news.ticker,
                news_id=news.id,
                url=news.url,
                title=news.title,
                date=news.date,
                feeling=feeling,
                version=self._version,
            )
        )

    def when(self, event: DomainEvent):
        event_type = event.type

        if event_type == "ASSET_FEELING_DETECTED":
            self.__when_feeling_detected(event)
        else:
            raise ValueError("Event not defined")

    def __when_feeling_detected(self, event: DomainEvent):
        if self.__state is None:
            raise ValueError("Incorrect transition from a previous state")

        self.__state = self.__state.with_feeling_detected(event)

    def get_state(self) -> PredictionState:
        return self.__state
