import json
from datetime import datetime, date
from typing import List

from google.cloud import pubsub_v1
from stock_api.domain.event_publisher import DomainEventPublisher
from stock_api.domain.events import DomainEvent
from stock_api.logger import get_logger

logger = get_logger(__name__)


def _serialize_datetime(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")


class PubSubEventPublisher(DomainEventPublisher):
    def __init__(self, project_id: str | None, topic: str | None):
        self._enabled = bool(project_id and topic)
        if not self._enabled:
            return

        self._publisher = pubsub_v1.PublisherClient()
        self._topic_path = self._publisher.topic_path(project_id, topic)

    def publish(self, events: List[DomainEvent], asset_id: str):
        if not self._enabled:
            return

        for event in events:
            event_payload = {
                "assetId": asset_id,
                "url": event.payload["url"],
                "newsId": event.payload["news_id"],
                "title": event.payload["title"],
                "date": event.payload["date"],
                "feeling": event.payload["feeling"],
            }

            payload = {
                "eventId": event.event_id,
                "occurredAt": event.occurred_at,
                "aggregateId": event.aggregate_id,
                "version": event.version,
                "type": event.type,
                "payload": event_payload,
            }

            message_bytes = json.dumps(
                payload,
                default=_serialize_datetime,
                separators=(",", ":"),
            ).encode("utf-8")

            future = self._publisher.publish(
                self._topic_path, message_bytes, type=event.type
            )

            future.result()
            logger.debug("Published event %s to %s", event.event_id, self._topic_path)
