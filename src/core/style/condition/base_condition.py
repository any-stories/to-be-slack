from abc import ABC, abstractmethod
from core.message.context import MessageContext


class BaseCondition(ABC):

    @abstractmethod
    def matches(
        self,
        context: MessageContext
    ) -> bool:
        pass
