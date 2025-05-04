import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DomainEvent:
    event_id: str
    occurred_at: str
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
    score: int,
    version: int,
) -> DomainEvent:
    payload = {
        "url": url,
        "news_id": news_id,
        "title": title,
        "date": date.isoformat(),
        "score": score,
    }

    return DomainEvent(
        event_id=str(uuid.uuid4()),
        occurred_at=datetime.now().isoformat(),
        aggregate_id=ticker,
        version=version,
        type="ASSET_FEELING_DETECTED",
        payload=payload,
    )
