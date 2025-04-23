from abc import ABC, abstractmethod
from stock_api.domain.events import DomainEvent

class DomainEventPublisher(ABC):
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        pass
