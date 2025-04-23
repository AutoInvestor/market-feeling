from typing import List
from stock_api.domain.events import DomainEvent

class EventSourcedEntity:
    def __init__(self, stream: List[DomainEvent] = None):
        self._uncommitted_events: List[DomainEvent] = []
        self._version = 0
        if stream:
            for e in stream:
                self._apply(e, is_new=False)
            self._version = len(stream)

    def _apply(self, event: DomainEvent, is_new: bool):
        handler = getattr(self, f"when_{event.type.lower()}", None)
        if not handler:
            raise ValueError(f"No handler for event type {event.type}")
        handler(event)
        if is_new:
            self._uncommitted_events.append(event)

    def apply(self, event: DomainEvent):
        self._apply(event, is_new=True)

    def get_uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)

    def mark_events_as_committed(self):
        self._uncommitted_events.clear()
