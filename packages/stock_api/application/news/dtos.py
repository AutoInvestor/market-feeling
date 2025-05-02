from dataclasses import dataclass
from datetime import datetime


@dataclass
class GetLatestNewsCommand:
    ticker: str


@dataclass
class PredictionResponse:
    score: int
    interpretation: str
    percentage_range: str

    @staticmethod
    def empty() -> "PredictionResponse":
        return PredictionResponse(
            score=0,
            interpretation="",
            percentage_range="",
        )


@dataclass
class LatestNews:
    id: str
    ticker: str
    date: datetime
    title: str
    url: str
    prediction: PredictionResponse

    @staticmethod
    def empty() -> "LatestNews":
        return LatestNews(
            id="",
            ticker="",
            date=datetime.min,
            title="",
            url="",
            prediction=PredictionResponse(
                score=0,
                interpretation="",
                percentage_range="",
            ),
        )

    def is_equal_to(self, other_id: str) -> bool:
        return self.id == other_id
