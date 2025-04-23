from abc import ABC, abstractmethod
from stock_api.domain.prediction import Prediction


class PredictionModel(ABC):
    @abstractmethod
    def get_prediction_from_text(self, text: str, company_name: str) -> Prediction:
        pass

    @abstractmethod
    def get_prediction_from_url(self, url: str, company_name: str) -> Prediction:
        pass
