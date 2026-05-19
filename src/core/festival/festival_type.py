from enum import StrEnum


class FestivalType(StrEnum):
    """
    Festival date calculation type.

    FIXED:
        Fixed solar calendar date.
        Example: 国庆节 10月1日

    LUNAR:
        Lunar calendar date.
        Example: 春节 正月初一

    WEEK:
        Nth weekday of a month.
        Example: 母亲节 5月第2个周日

    TERM:
        Solar term based festival.
        Example: 清明节
    """

    FIXED = "fixed"

    LUNAR = "lunar"

    WEEK = "week"

    TERM = "term"
