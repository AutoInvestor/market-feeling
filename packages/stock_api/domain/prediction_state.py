from dataclasses import dataclass
from datetime import datetime

@dataclass
class PredictionState:
    id: str = ""
    ticker: str = ""
    date: datetime = None
    title: str = ""
    url: str = ""
    score: int = 5
    interpretation: str = ""
    percentage_range: str = ""

    _interpretations = {
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

    _percentage_ranges = {
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

    def apply_score(self, raw_score: float):
        """Round, clamp, and set interpretation/range in one go."""
        try:
            score = int(round(raw_score))
        except TypeError:
            raise ValueError(f"Score must be numeric (got {raw_score!r})")
        score = max(0, min(10, score))

        self.score = score
        self.interpretation = self._interpretations[score]
        self.percentage_range = self._percentage_ranges[score]
