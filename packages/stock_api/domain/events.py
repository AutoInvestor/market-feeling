import uuid, time
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DomainEvent:
    event_id: str
    occurred_at: int
    aggregate_id: str
    version: int
    type: str
    payload: dict


def make_first_prediction_for_ticker_event(ticker: str) -> DomainEvent:
    return DomainEvent(
        event_id=str(uuid.uuid4()),
        occurred_at=int(time.time()),
        aggregate_id=ticker,
        version=0,
        type="FIRST_TICKER_PREDICTION",
        payload={},
    )


def make_asset_feeling_detected_event(
    ticker: str, url: str, title: str, date: datetime, score: int, version: int
) -> DomainEvent:
    payload = {"url": url, "title": title, "date": date.isoformat(), "score": score}

    return DomainEvent(
        event_id=str(uuid.uuid4()),
        occurred_at=int(time.time()),
        aggregate_id=ticker,
        version=version,
        type="ASSET_FEELING_DETECTED",
        payload=payload,
    )
