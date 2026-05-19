from dataclasses import dataclass

from core.style.condition.base_condition import BaseCondition
from core.message.context import MessageContext

@dataclass(slots=True)
class WeekdayCondition(BaseCondition):

    weekdays: set[int]

    def matches(
        self,
        context: MessageContext
    ) -> bool:
        return context.business_time.weekday() in self.weekdays