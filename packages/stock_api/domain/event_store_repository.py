from abc import ABC, abstractmethod
from typing import List
from stock_api.domain.events import DomainEvent


class EventStoreRepository(ABC):
    @abstractmethod
    def append(self, event: DomainEvent) -> None:
        pass

    @abstractmethod
    def get_events(self, aggregate_id: str) -> List[DomainEvent]:
        pass
