from dataclasses import dataclass
import datetime
from core.style.condition.base_condition import BaseCondition


@dataclass(slots=True)
class MessageTone:

    header: str

    footer: str

    conditions: list[BaseCondition] | None = None

    def is_available(
        self,
        dt: datetime.datetime,
    ) -> bool:

        if not self.conditions:
            return True

        return all(
            condition.matches(dt)
            for condition in self.conditions
        )