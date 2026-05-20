from dataclasses import dataclass

from core.message.conditions.condition import Condition
from core.message.models.context import MessageContext


@dataclass(slots=True, kw_only=True)
class MonthCondition(Condition):

    months: set[int]

    def matches(
        self,
        context: MessageContext
    ) -> bool:

        return context.business_time.month in self.months