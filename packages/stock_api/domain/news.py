from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class News:
    id: str = ""
    ticker: str = ""
    date: datetime = field(default_factory=datetime.now)
    title: str = "No news found"
    url: str = ""
