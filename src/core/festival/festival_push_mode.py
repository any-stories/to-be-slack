from enum import StrEnum


class FestivalPushMode(StrEnum):

    ALL = "all"

    PUBLIC_HOLIDAYS_ONLY = "public_holidays_only"

    RANDOM = "random"

    @classmethod
    def from_value(
        cls,
        value: str | None,
    ) -> "FestivalPushMode":

        if value is None:
            return cls.ALL

        try:
            return cls(value)

        except ValueError:
            return cls.ALL
