from dataclasses import dataclass

from core.message.conditions.condition import Condition
from core.message.models.context import MessageContext
from core.enums.day_period import DayPeriod


@dataclass(slots=True, kw_only=True)
class DayPeriodCondition(Condition):

    periods: set[DayPeriod]

    def matches(
        self,
        context: MessageContext
    ) -> bool:
        business_time = context.business_time
        return DayPeriod.from_hour(business_time.hour) in self.periods