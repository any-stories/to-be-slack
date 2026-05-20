from dataclasses import dataclass, field

from core.message.models.context import MessageContext
from core.message.conditions.condition import Condition


@dataclass(slots=True, kw_only=True)
class MessageComponent:
    bias: float = 1.0
    conditions: list[Condition] = field(default_factory=list)

    def is_available(self, context: MessageContext) -> bool:
        if not self.conditions or context is None:
            return True
        return all(condition.matches(context) for condition in self.conditions)

    def score(self, context: MessageContext) -> float:
        if not self.conditions or context is None:
            return self.bias

        condition_score = sum(condition.score(context) for condition in self.conditions)
        return self.bias * condition_score
