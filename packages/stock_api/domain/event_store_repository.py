from abc import ABC, abstractmethod
from typing import Optional
from stock_api.domain.prediction_aggregate import PredictionAggregate


class EventStoreRepository(ABC):
    @abstractmethod
    def save(self, prediction: PredictionAggregate):
        pass

    @abstractmethod
    def find_by_id(self, ticker: str) -> Optional[PredictionAggregate]:
        pass
