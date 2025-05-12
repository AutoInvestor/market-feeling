from stock_api.infrastructure.listeners.pubsub_event import PubSubEventDTO


class PubSubEventMapper:
    @staticmethod
    def from_dict(data: dict) -> PubSubEventDTO:
        return PubSubEventDTO(
            event_id=data["eventId"],
            aggregate_id=data["aggregateId"],
            occurred_at=data["occurredAt"],
            version=data["version"],
            type=data["type"],
            payload=data["payload"],
        )
