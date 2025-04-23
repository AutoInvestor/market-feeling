from stock_api.domain.event_publisher import DomainEventPublisher
from stock_api.domain.events import DomainEvent
from stock_api.logger import get_logger

logger = get_logger(__name__)


class InMemoryDomainEventPublisher(DomainEventPublisher):
    def __init__(self):
        self.published_events: list[DomainEvent] = []
        logger.info("Initialized InMemoryDomainEventPublisher")

    def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)

        logger.info(
            "Published event %s for aggregate %s (version=%d)",
            event.type,
            event.aggregate_id,
            event.version,
        )
