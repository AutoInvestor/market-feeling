import json
from google.cloud import pubsub_v1
from stock_api.domain.event_publisher import DomainEventPublisher
from stock_api.domain.events import DomainEvent
from stock_api.logger import get_logger

logger = get_logger(__name__)


class PubSubEventPublisher(DomainEventPublisher):
    def __init__(self, project_id: str, topic: str):
        self._publisher = pubsub_v1.PublisherClient()
        self._topic_path = self._publisher.topic_path(project_id, topic)
        logger.info("Initialized PubSub publisher on %s", self._topic_path)

    def publish(self, event: DomainEvent) -> None:
        message = json.dumps(
            {
                "eventId": event.event_id,
                "occurredAt": event.occurred_at,
                "aggregateId": event.aggregate_id,
                "version": event.version,
                "type": event.type,
                "payload": event.payload,
            }
        ).encode("utf-8")
        future = self._publisher.publish(self._topic_path, message, type=event.type)
        result = future.result()
        logger.info(
            "Published to Pub/Sub message_id=%s for %s v=%d",
            result,
            event.type,
            event.version,
        )
