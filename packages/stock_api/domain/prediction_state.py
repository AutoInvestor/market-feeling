from dataclasses import dataclass
from datetime import datetime

from stock_api.domain.events import DomainEvent


@dataclass
class PredictionState:
    ticker: str = ""
    date: datetime = None
    news_id: str = ""
    title: str = ""
    url: str = ""
    feeling: int = 0

    @staticmethod
    def empty() -> "PredictionState":
        return PredictionState()

    @staticmethod
    def with_feeling_detected(event: DomainEvent) -> "PredictionState":
        payload = event.payload

        feeling = int(round(payload["feeling"]))
        feeling = max(0, min(10, feeling))

        return PredictionState(
            ticker=event.aggregate_id,
            date=payload["date"],
            news_id=payload["news_id"],
            title=payload["title"],
            url=payload["url"],
            feeling=feeling,
        )
