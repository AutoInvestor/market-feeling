from dataclasses import dataclass
from datetime import datetime


@dataclass
class PubSubEventDTO:
    event_id: str
    aggregate_id: str
    occurred_at: datetime
    version: int
    type: str
    payload: dict
