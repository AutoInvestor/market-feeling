from typing import List
from stock_api.domain.event_store_repository import EventStoreRepository
from stock_api.domain.events import DomainEvent
from stock_api.domain.exceptions import ConcurrencyError


class InMemoryEventStoreRepository(EventStoreRepository):
    def __init__(self):
        self._events: dict[str, List[DomainEvent]] = {}

    def append(
        self,
        aggregate_id: str,
        events: List[DomainEvent],
        expected_version: int,
    ) -> None:
        """
        Only append if the current version (number of stored events)
        matches expected_version; otherwise raise ConcurrencyError.
        """
        current = self._events.get(aggregate_id, [])
        current_version = len(current)

        if current_version != expected_version:
            raise ConcurrencyError(
                f"[InMemory] Stream {aggregate_id} at version {current_version}, "
                f"but expected {expected_version}"
            )

        self._events.setdefault(aggregate_id, []).extend(events)

    def get_events(self, aggregate_id: str) -> List[DomainEvent]:
        return list(self._events.get(aggregate_id, []))
