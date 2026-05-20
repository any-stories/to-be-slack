from dataclasses import dataclass
from core.message.conditions.condition import Condition
from core.message.models.context import MessageContext


@dataclass(slots=True, kw_only=True)
class FestivalCondition(Condition):

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
