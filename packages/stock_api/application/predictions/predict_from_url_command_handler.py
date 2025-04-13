from dataclasses import dataclass
from stock_api.domain.prediction import Prediction


@dataclass
class PredictFromURLCommand:
    ticker: str
    url: str


@dataclass
class PredictionScore:
    ticker: str
    score: int
    interpretation: str
    percentage_range: str


class PredictFromURLCommandHandler:
    def __init__(self):
        pass

    def handle(self, command: PredictFromURLCommand) -> PredictionScore:
        prediction = Prediction(
            score=4, interpretation="Significant rise", percentage_range="20% to 29%"
        )

        return PredictionScore(
            ticker=command.ticker,
            score=prediction.score,
            interpretation=prediction.interpretation,
            percentage_range=prediction.percentage_range,
        )
