from abc import ABC, abstractmethod

from stock_api.domain.raw_score import RawScore


class PredictionModel(ABC):
    @abstractmethod
    def get_prediction_from_text(self, text: str, company_name: str) -> RawScore:
        pass

    @abstractmethod
    def get_prediction_from_url(self, url: str, company_name: str) -> RawScore:
        pass
