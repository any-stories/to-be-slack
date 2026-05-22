from dataclasses import dataclass, field
from core.message.conditions.condition import Condition
from core.message.models.context import MessageContext


@dataclass(slots=True, kw_only=True)
class FestivalCondition(Condition):
    festival_names: set[str] = field(default_factory=set)
    festival_keywords: set[str] = field(default_factory=set)

    def matches(self, context: MessageContext) -> bool:
        festival_names = (
            context.day_status.festival_names
            if context.day_status and context.day_status.festival_names
            else []
        )

        for festival_name in festival_names:

            if festival_name in self.festival_names:
                return True

            if any(keyword in festival_name for keyword in self.festival_keywords):
                return True

        return False
