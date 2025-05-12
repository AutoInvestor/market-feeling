from dataclasses import dataclass


@dataclass
class PubSubEventDTO:
    event_id: str
    aggregate_id: str
    occurred_at: str
    version: int
    type: str
    payload: dict
