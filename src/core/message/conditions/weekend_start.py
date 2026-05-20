from dataclasses import dataclass

from core.message.models.context import MessageContext
from core.message.conditions.condition import Condition


@dataclass(slots=True, kw_only=True)
class WeekendStartCondition(Condition):

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