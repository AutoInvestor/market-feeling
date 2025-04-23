import uuid, time
from dataclasses import dataclass

@dataclass
class DomainEvent:
    event_id: str
    occurred_at: int
    aggregate_id: str
    version: int
    type: str
    payload: dict

def make_asset_feeling_detected_event(
    aggregate_id: str,
    version: int,
    payload: dict
) -> DomainEvent:
    return DomainEvent(
        event_id=str(uuid.uuid4()),
        occurred_at=int(time.time()),
        aggregate_id=aggregate_id,
        version=version,
        type="ASSET_FEELING_DETECTED",
        payload=payload,
    )
