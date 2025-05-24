from abc import ABC, abstractmethod
from typing import List

from stock_api.domain.events import DomainEvent


class DomainEventPublisher(ABC):
    @abstractmethod
    def publish(self, events: List[DomainEvent], asset_id: str):
        pass
