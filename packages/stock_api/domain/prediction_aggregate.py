from typing import List
from datetime import datetime

from stock_api.application.news.get_latest_news_command_handler import LatestNews
from stock_api.domain.event_sourced_entity import EventSourcedEntity
from stock_api.domain.events import DomainEvent, make_asset_feeling_detected_event
from stock_api.domain.prediction_state import PredictionState


class PredictionAggregate(EventSourcedEntity):
    def __init__(self, stream: List[DomainEvent] = None):
        super().__init__(stream)
        self.state = PredictionState()

    @staticmethod
    def detect(
        latest_news: "LatestNews", past_events: List[DomainEvent], raw_score: int
    ) -> "PredictionAggregate":
        agg = PredictionAggregate(stream=past_events)
        version = len(past_events) + 1

        payload = {
            "id": latest_news.id,
            "ticker": latest_news.ticker,
            "date": latest_news.date.isoformat(),
            "title": latest_news.title,
            "url": latest_news.url,
            "raw_score": raw_score,
        }
        evt = make_asset_feeling_detected_event(
            aggregate_id=latest_news.id,
            version=version,
            payload=payload,
        )
        agg.apply(evt)
        return agg

    def when_asset_feeling_detected(self, event: DomainEvent):
        p = event.payload
        self.state.id = p["id"]
        self.state.ticker = p["ticker"]
        self.state.date = datetime.fromisoformat(p["date"])
        self.state.title = p["title"]
        self.state.url = p["url"]
        self.state.apply_score(p["raw_score"])
