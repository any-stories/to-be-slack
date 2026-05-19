from dataclasses import dataclass
from core.style.condition.base_condition import BaseCondition
from core.message.context import MessageContext


@dataclass(slots=True)
class FestivalCondition(BaseCondition):

    festival_names: set[str]

    def matches(
        self,
        context: MessageContext
    ) -> bool:
        day_festivals = (
            context.day_status.festival_names
            if context.day_status and context.day_status.festival_names
            else []
        )

        return any(name in self.festival_names for name in day_festivals)
