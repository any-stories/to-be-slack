from dataclasses import dataclass

from core.message.context import MessageContext
from core.style.condition.base_condition import BaseCondition


@dataclass(slots=True)
class WeekendStartCondition(BaseCondition):

    def matches(
        self,
        context: MessageContext,
    ) -> bool:

        friday = context.weekend_status.friday
        tomorrow = context.weekend_status.tomorrow

        return (
            friday.is_today
            and not tomorrow.is_workday
        )