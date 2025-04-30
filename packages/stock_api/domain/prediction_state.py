from dataclasses import dataclass
from datetime import datetime

from stock_api.domain.events import DomainEvent


@dataclass
class PredictionState:
    ticker: str = ""
    date: datetime = None
    title: str = ""
    url: str = ""
    score: int = 5
    interpretation: str = ""
    percentage_range: str = ""

    INTERPRETATIONS = {
        0: "Very sharp drop",
        1: "Significant drop",
        2: "Moderate drop",
        3: "Slight drop",
        4: "Very slight drop",
        5: "No significant change",
        6: "Very slight rise",
        7: "Slight rise",
        8: "Moderate rise",
        9: "Significant rise",
        10: "Very sharp rise",
    }

    RANGE = {
        0: "≤ -2.5%",
        1: "-2% a -2.5%",
        2: "-1.5% a -2%",
        3: "-1% a -1.5%",
        4: "-0.5% a -1%",
        5: "±0.5%",
        6: "+0.5% a +1%",
        7: "+1% a +1.5%",
        8: "+1.5% a +2%",
        9: "+2% a +2.5%",
        10: "≥ +2.5%",
    }

    @staticmethod
    def empty() -> "PredictionState":
        return PredictionState()

    def get_aggregate_id(self) -> str:
        return self.ticker

    def is_empty(self) -> bool:
        return self.ticker == ""

    @staticmethod
    def get_interpretation_from_score(score: int) -> str:
        return PredictionState.INTERPRETATIONS[score]

    @staticmethod
    def get_range_from_score(score: int) -> str:
        return PredictionState.RANGE[score]

    @staticmethod
    def with_prediction_created(event: DomainEvent) -> "PredictionState":
        return PredictionState(ticker=event.aggregate_id)

    @staticmethod
    def with_feeling_detected(event: DomainEvent) -> "PredictionState":
        payload = event.payload

        score = int(round(payload["score"]))
        score = max(0, min(10, score))

        return PredictionState(
            ticker=event.aggregate_id,
            date=payload["date"],
            title=payload["title"],
            url=payload["url"],
            score=score,
            interpretation=PredictionState.INTERPRETATIONS[score],
            percentage_range=PredictionState.RANGE[score],
        )
