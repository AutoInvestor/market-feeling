from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class GetLatestNewsCommand:
    ticker: str

@dataclass(frozen=True)
class PredictionResponse:
    score: int
    interpretation: str
    percentage_range: str

@dataclass(frozen=True)
class LatestNews:
    id: str
    ticker: str
    date: datetime
    title: str
    url: str
    prediction: PredictionResponse
