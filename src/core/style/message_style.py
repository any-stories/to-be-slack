from enum import StrEnum


class MessageStyle(StrEnum):

    DEFAULT = "default"

    ROMANTIC = "romantic"

    POETIC = "poetic"

    @classmethod
    def from_value(
        cls,
        value: str | None,
    ) -> "MessageStyle":

        if value is None:
            return cls.DEFAULT

        try:
            return cls(value)

        except ValueError:
            return cls.DEFAULT
