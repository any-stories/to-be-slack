from dataclasses import dataclass

from core.style.season import Season
from core.style.condition.base_condition import BaseCondition
from core.message.context import MessageContext


def month_to_season(month: int) -> Season:
    if month in (3, 4, 5):
        return Season.SPRING
    if month in (6, 7, 8):
        return Season.SUMMER
    if month in (9, 10, 11):
        return Season.AUTUMN
    return Season.WINTER


@dataclass(slots=True)
class SeasonCondition(BaseCondition):
    seasons: set[Season]

    def matches(self, context: MessageContext) -> bool:
        season = month_to_season(context.business_time.month)
        return season in self.seasons
