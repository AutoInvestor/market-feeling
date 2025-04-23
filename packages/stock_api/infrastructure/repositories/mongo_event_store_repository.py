from pymongo import MongoClient
from stock_api.domain.event_store_repository import EventStoreRepository
from stock_api.domain.events import DomainEvent


class MongoEventStoreRepository(EventStoreRepository):
    def __init__(self, uri: str, db_name: str):
        client = MongoClient(uri)
        self._coll = client[db_name]["events"]

    def append(self, event: DomainEvent) -> None:
        doc = {
            "_id": event.event_id,
            "occurred_at": event.occurred_at,
            "aggregate_id": event.aggregate_id,
            "version": event.version,
            "type": event.type,
            "payload": event.payload,
        }
        self._coll.insert_one(doc)

    def get_events(self, aggregate_id: str) -> list[DomainEvent]:
        cursor = self._coll.find({"aggregate_id": aggregate_id}).sort("version", 1)
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
