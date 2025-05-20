import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class DomainEvent:
    event_id: str
    occurred_at: datetime
    aggregate_id: str
    version: int
    type: str
    payload: dict


def make_asset_feeling_detected_event(
    ticker: str,
    url: str,
    news_id: str,
    title: str,
    date: datetime,
    feeling: int,
    version: int,
) -> DomainEvent:
    payload = {
        "url": url,
        "news_id": news_id,
        "title": title,
        "date": date,
        "feeling": feeling,
    }

    return DomainEvent(
        event_id=str(uuid.uuid4()),
        occurred_at=datetime.now(timezone.utc),
        aggregate_id=ticker,
        version=version,
        type="ASSET_FEELING_DETECTED",
        payload=payload,
    )
