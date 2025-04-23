from stock_api.domain.event_store_repository import EventStoreRepository
from stock_api.domain.events import DomainEvent


class InMemoryEventStoreRepository(EventStoreRepository):
    def __init__(self):
        self._events: dict[str, list[DomainEvent]] = {}

    def append(self, event: DomainEvent) -> None:
        self._events.setdefault(event.aggregate_id, []).append(event)

    def get_events(self, aggregate_id: str) -> list[DomainEvent]:
        return list(self._events.get(aggregate_id, []))
