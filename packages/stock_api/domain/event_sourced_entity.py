from abc import abstractmethod
from typing import List
from stock_api.domain.events import DomainEvent


class EventSourcedEntity:

    def __init__(self, stream: List[DomainEvent]):
        self._uncommitted_events: List[DomainEvent] = []
        self._version = 0
        if stream:
            for e in stream:
                self.when(e)
            self._version = len(stream)

    @abstractmethod
    def when(self, event: DomainEvent):
        pass

    def apply(self, event: DomainEvent):
        self._uncommitted_events.append(event)
        self.when(event)

    def get_uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)

    def mark_events_as_committed(self):
        self._uncommitted_events.clear()
