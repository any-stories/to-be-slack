from dataclasses import dataclass
import datetime


@dataclass(slots=True)
class DayStatus:
    date: datetime.date

    weekday_cn_short: str

    is_weekend: bool

    is_workday: bool

    is_holiday: bool

    holiday_name: str | None

    festival_names: tuple[str, ...] = ()
