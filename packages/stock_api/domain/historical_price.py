from dataclasses import dataclass
from datetime import date


@dataclass
class HistoricalPrice:
    date: date
    open: float
    close: float
