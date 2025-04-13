from dataclasses import dataclass
from datetime import datetime
from stock_api.domain.prediction import Prediction


@dataclass
class News:
    id: str
    ticker: str
    date: datetime
    title: str
    url: str
    prediction: Prediction
