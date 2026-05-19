from dataclasses import dataclass

from core.style.condition.base_condition import BaseCondition
from core.message.context import MessageContext
from core.style.day_period import DayPeriod


@dataclass(slots=True)
class DayPeriodCondition(BaseCondition):

    periods: set[DayPeriod]

    def matches(
        self,
        context: MessageContext
    ) -> bool:
        business_time = context.business_time
        return DayPeriod.from_hour(business_time.hour) in self.periods