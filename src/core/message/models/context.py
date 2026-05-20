from dataclasses import dataclass
import datetime

from core.calendar.lunar_protocol import LunarDateProtocol
from core.calendar.models import DayStatus, WeekendStatus


@dataclass(slots=True)
class MessageContext:
    business_time: datetime.datetime

    day_status: DayStatus

    lunar_date: LunarDateProtocol

    year_progress: float

    weekend_status: WeekendStatus

    # festivals: tuple[Festival, ...]

    # one_sentence: dict[str, Any] | None = None
