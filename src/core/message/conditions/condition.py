from abc import ABC, abstractmethod
from dataclasses import dataclass

from core.message.models.context import MessageContext

@dataclass(kw_only=True)
class Condition(ABC):
    weight: float = 1.0

    @abstractmethod
    def matches(self, context: MessageContext) -> bool:
        pass

    def score(self, context: MessageContext) -> float:
        return self.weight if self.matches(context) else 0.0
