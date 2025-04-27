from pymongo import MongoClient
from stock_api.domain.event_store_repository import EventStoreRepository
from stock_api.domain.events import DomainEvent
from stock_api.domain.exceptions import ConcurrencyError
from stock_api.logger import get_logger

logger = get_logger(__name__)

class MongoEventStoreRepository(EventStoreRepository):
    def __init__(self, uri: str | None, db_name: str):
        """
        If uri is empty or None, this repository becomes a no-op stub:
          - append() does nothing
          - get_events() always returns []
        """
        self._enabled = bool(uri)
        if not self._enabled:
            logger.warning(
                "No MONGODB_URI provided: MongoEventStoreRepository disabled, using dummy behavior."
            )
            return

        client = MongoClient(uri)
        self._coll = client[db_name]["events"]

    def append(
        self,
        aggregate_id: str,
        events: list[DomainEvent],
        expected_version: int,
    ) -> None:
        if not self._enabled:
            return

        # 1) find the highest existing version
        latest = (
            self._coll
            .find({"aggregate_id": aggregate_id}, {"version": 1})
            .sort("version", -1)
            .limit(1)
            .next(None)
        )
        current_version = latest["version"] if latest else 0

        # 2) optimistic‐concurrency check
        if current_version != expected_version:
            raise ConcurrencyError(
                f"Stream {aggregate_id} at version {current_version}, "
                f"but expected {expected_version}"
            )

        # 3) insert all new events in one batch
        docs = []
        for evt in events:
            docs.append({
                "_id": evt.event_id,
                "occurred_at": evt.occurred_at,
                "aggregate_id": evt.aggregate_id,
                "version": evt.version,
                "type": evt.type,
                "payload": evt.payload,
            })
        self._coll.insert_many(docs)

    def get_events(self, aggregate_id: str) -> list[DomainEvent]:
        if not self._enabled:
            return []

        cursor = (
            self._coll
            .find({"aggregate_id": aggregate_id})
            .sort("version", 1)
        )
        return [
            DomainEvent(
                event_id=doc["_id"],
                occurred_at=doc["occurred_at"],
                aggregate_id=doc["aggregate_id"],
                version=doc["version"],
                type=doc["type"],
                payload=doc["payload"],
            )
            for doc in cursor
        ]
