from dataclasses import dataclass

from core.enums.festival_type import FestivalType


@dataclass(
    frozen=True,
    slots=True,
)
class Festival:

    name: str

    type: FestivalType

    month: int | None = None

    day: int | None = None

    nth: int | None = None

    weekday: int | None = None

    term_name: str | None = None

    enabled: bool = True

    is_public_holiday: bool = False
