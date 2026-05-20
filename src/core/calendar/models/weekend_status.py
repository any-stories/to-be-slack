from dataclasses import dataclass
import datetime


@dataclass(slots=True)
class FridayStatus:
    """
    Current week's Friday status.
    """

    date: datetime.date

    days_until: int

    is_today: bool


@dataclass(slots=True)
class TomorrowStatus:
    """
    Tomorrow workday status.
    """

    date: datetime.date

    is_workday: bool


@dataclass(slots=True)
class NextFridayStatus:
    """
    Next Friday status when current Friday has passed.
    """

    date: datetime.date

    days_until: int


@dataclass(slots=True)
class WeekendStatus:
    """
    Weekend related status information.

    Includes:
    - current Friday info
    - tomorrow workday info
    - next Friday info (optional)
    """

    friday: FridayStatus

    tomorrow: TomorrowStatus

    next_friday: NextFridayStatus | None = None
