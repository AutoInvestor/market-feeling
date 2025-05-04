from abc import ABC, abstractmethod

from stock_api.domain.raw_feeling import RawFeeling


class PredictionModel(ABC):
    @abstractmethod
    def get_prediction_from_text(self, text: str, company_name: str) -> RawFeeling:
        pass

    @abstractmethod
    def get_prediction_from_url(self, url: str, company_name: str) -> RawFeeling:
        pass
