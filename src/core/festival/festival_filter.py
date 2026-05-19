import random

from core.festival.festival import (
    Festival,
)
from core.festival.festival_push_mode import (
    FestivalPushMode,
)


def filter_festivals(
    festivals: tuple[Festival, ...],
    mode: FestivalPushMode,
) -> tuple[Festival, ...]:
    enabled = tuple(festival for festival in festivals if festival.enabled)
    if mode == FestivalPushMode.ALL:
        return enabled
    if mode == (FestivalPushMode.PUBLIC_HOLIDAYS_ONLY):
        return tuple(festival for festival in enabled if (festival.is_public_holiday))

    if mode == FestivalPushMode.RANDOM:
        selected_mode = random.choice(
            [
                FestivalPushMode.ALL,
                FestivalPushMode.PUBLIC_HOLIDAYS_ONLY,
            ]
        )
        return filter_festivals(
            enabled,
            selected_mode,
        )
    return enabled
