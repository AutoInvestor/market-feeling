from stock_api.domain.event_publisher import DomainEventPublisher
from stock_api.domain.events import DomainEvent

class InMemoryDomainEventPublisher(DomainEventPublisher):
    def __init__(self):
        self.published_events: list[DomainEvent] = []

    def publish(self, event: DomainEvent) -> None:
        # (TODO) simulate external queue

        self.published_events.append(event)

        # (optional) logging
        print(f"[EventBus] Published {event.type} for {event.aggregate_id}")
