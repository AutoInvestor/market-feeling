from dataclasses import dataclass


@dataclass
class Prediction:
    score: int
    interpretation: str
    percentage_range: str
