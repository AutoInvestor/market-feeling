from typing import List

from pymongo import MongoClient
from stock_api.domain.event_store_repository import EventStoreRepository
from stock_api.domain.events import DomainEvent
from stock_api.domain.prediction_aggregate import PredictionAggregate
from stock_api.logger import get_logger

logger = get_logger(__name__)


class MongoEventStoreRepository(EventStoreRepository):
    def __init__(self, uri: str | None, db_name: str):
        self._enabled = bool(uri)
        if not self._enabled:
            logger.warning(
                "No MONGODB_URI provided: MongoEventStoreRepository disabled, using dummy behavior."
            )
            return

        client = MongoClient(uri)
        self._coll = client[db_name]["events"]

    def save(self, prediction: PredictionAggregate):
        if not self._enabled:
            return

        events = prediction.get_uncommitted_events()

        docs = []
        for event in events:
            docs.append(
                {
                    "event_id": event.event_id,
                    "occurred_at": event.occurred_at,
                    "aggregate_id": event.aggregate_id,
                    "version": event.version,
                    "type": event.type,
                    "payload": event.payload,
                }
            )
        self._coll.insert_many(docs)

    def find_by_id(self, ticker: str) -> PredictionAggregate:
        if not self._enabled:
            return PredictionAggregate.empty()

        cursor = self._coll.find({"aggregate_id": ticker}).sort("version", 1)

        events_for_aggregate: List[DomainEvent] = []
        for doc in cursor:
            event = DomainEvent(
                event_id=doc["event_id"],
                occurred_at=doc["occurred_at"],
                aggregate_id=doc["aggregate_id"],
                version=doc["version"],
                type=doc["type"],
                payload=doc["payload"],
            )
            events_for_aggregate.append(event)

        if not events_for_aggregate:
            PredictionAggregate.empty()

        return PredictionAggregate.from_events(events_for_aggregate)
