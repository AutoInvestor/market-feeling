from dataclasses import dataclass
from datetime import datetime


@dataclass
class GetLatestNewsCommand:
    ticker: str


@dataclass
class LatestNews:
    id: str
    ticker: str
    date: datetime
    title: str
    url: str
    feeling: int

    @staticmethod
    def empty() -> "LatestNews":
        return LatestNews(
            id="",
            ticker="",
            date=datetime.min,
            title="",
            url="",
            feeling=0,
        )
