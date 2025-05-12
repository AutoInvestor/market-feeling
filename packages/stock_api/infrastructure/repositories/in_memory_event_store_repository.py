from typing import List
from stock_api.domain.event_store_repository import EventStoreRepository
from stock_api.domain.events import DomainEvent
from stock_api.domain.prediction_aggregate import PredictionAggregate


class InMemoryEventStoreRepository(EventStoreRepository):
    def __init__(self):
        self.__event_store: List[DomainEvent] = []

    def save(self, prediction: PredictionAggregate):
        events = prediction.get_uncommitted_events()
        for event in events:
            self.__event_store.append(event)

    def find_by_id(self, ticker: str) -> PredictionAggregate:
        events_for_aggregate: List[DomainEvent] = [
            event for event in self.__event_store if event.aggregate_id == ticker
        ]

        if not events_for_aggregate:
            return PredictionAggregate.empty()

        return PredictionAggregate.from_events(events_for_aggregate)
