import calendar
import datetime
from functools import lru_cache
from typing import TypeAlias

from borax.calendars.festivals2 import FestivalLibrary, SolarFestival
from borax.calendars.lunardate import LunarDate, TermUtils

from core.calendar.models import Festival
from core.enums import FestivalType
from utils.logger import setup_logger

log = setup_logger("calendar")

# Supported date input types
DateLike: TypeAlias = datetime.date | datetime.datetime | str


class CalendarUtil:
    """Calendar and festival utility methods."""

    # Monthly Valentine's Day themes
    VALENTINE_FESTIVALS = {
        1: "日记情人节",
        3: "白色情人节",
        4: "黑色情人节",
        5: "玫瑰情人节",
        6: "电影情人节",
        7: "银色情人节",
        8: "绿色情人节",
        9: "音乐情人节",
        10: "葡萄酒情人节",
        11: "电影情人节",
        12: "拥抱情人节",
    }

    EXTRA_FESTIVALS = (
        SolarFestival(month=6, day=18, name="电商年中大促"),
        SolarFestival(month=10, day=24, name="1024"),
        SolarFestival(month=11, day=11, name="双十一"),
        SolarFestival(month=12, day=12, name="双十二"),
    )

    @classmethod
    @lru_cache(maxsize=1)
    def _get_festival_library(cls) -> FestivalLibrary:
        """
        Load and cache festival library.

        Uses lru_cache to avoid repeated initialization.
        """
        festival_library = FestivalLibrary.load_builtin("ext1")

        monthly_valentines = [
            SolarFestival(month=month, day=14, name=name)
            for month, name in cls.VALENTINE_FESTIVALS.items()
        ]

        festival_library.extend(
            [
                *monthly_valentines,
                *cls.EXTRA_FESTIVALS,
            ]
        )

        return festival_library

    @staticmethod
    def normalize_date(date: DateLike | None = None) -> datetime.date:
        """
        Convert supported input types into datetime.date.

        Supported types:
        - datetime.date
        - datetime.datetime
        - YYYY-MM-DD string
        """
        if date is None:
            return datetime.date.today()

        if isinstance(date, datetime.datetime):
            return date.date()

        if isinstance(date, datetime.date):
            return date

        if isinstance(date, str):
            try:
                return datetime.date.fromisoformat(date)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid date format: {date}, expected YYYY-MM-DD"
                ) from exc

        raise TypeError("date must be date, datetime, or YYYY-MM-DD string")

    @classmethod
    def matches_weekday(cls, date: DateLike, weekday: int) -> bool:
        """
        Check whether a date matches the given weekday.

        weekday:
            0 = Monday
            6 = Sunday
        """
        if weekday not in range(7):
            raise ValueError("weekday must be between 0 and 6")

        return cls.normalize_date(date).weekday() == weekday

    @classmethod
    def is_friday(cls, date: DateLike) -> bool:
        """Check whether the given date is Friday."""
        return cls.matches_weekday(date, weekday=4)

    @classmethod
    def get_week_friday(
        cls,
        date: DateLike | None = None,
    ) -> datetime.date:
        """
        Get Friday of the week containing the given date.
        """
        normalized_date = cls.normalize_date(date)

        return normalized_date + datetime.timedelta(
            days=(4 - normalized_date.weekday())
        )

    @staticmethod
    def get_nth_weekday(
        year: int,
        month: int,
        nth: int,
        weekday: int,
    ) -> datetime.date:
        """
        Get the nth weekday in a month.

        Example:
            2nd Sunday of May
        """
        if nth <= 0:
            raise ValueError("nth must be greater than 0")

        first_weekday, days_in_month = calendar.monthrange(year, month)

        # Offset from first day of month to target weekday
        weekday_offset = (weekday - first_weekday) % 7

        target_day = 1 + weekday_offset + (nth - 1) * 7

        if target_day > days_in_month:
            raise ValueError(f"No {nth}-th weekday {weekday} in {year}-{month}")

        return datetime.date(year, month, target_day)

    @classmethod
    def get_lunar_date(
        cls,
        date: DateLike | None = None,
    ) -> LunarDate:
        """Convert solar date to lunar date."""
        return LunarDate.from_solar(cls.normalize_date(date))

    @classmethod
    def get_festival_names(
        cls,
        date: datetime.date,
    ) -> list[str]:
        """
        Get all festival names for the given date.
        """
        try:
            # 节气
            # lunar_date = LunarDate.from_solar_date(target_date)
            return cls._get_festival_library().get_festival_names(date)
        except ValueError:
            log.exception("Failed to get festival names")
            return []

    @classmethod
    def resolve_festival_date(
        cls,
        festival: Festival,
        year: int,
    ) -> datetime.date | None:
        """
        Resolve a festival definition into an actual date.
        """
        match festival:
            case Festival(
                type=FestivalType.FIXED,
                month=month,
                day=day,
            ):
                return datetime.date(year, month, day)

            case Festival(
                type=FestivalType.LUNAR,
                month=month,
                day=day,
            ):
                return LunarDate(year, month, day).to_solar_date()

            case Festival(
                type=FestivalType.WEEK,
                month=month,
                nth=nth,
                weekday=weekday,
            ):
                return cls.get_nth_weekday(year, month, nth, weekday)

            case Festival(
                type=FestivalType.TERM,
                nth=nth,
                term_name=term,
            ):
                return TermUtils.nth_term_day(year, nth, term)

        return None

    @classmethod
    def get_upcoming_festivals(
        cls,
        date: DateLike | None = None,
        festivals: tuple[Festival, ...] | None = None,
    ) -> list[dict]:
        """
        Get upcoming festivals after the given date.

        Returns:
            [
                {
                    "name": str,
                    "date": datetime.date,
                    "days": int,
                }
            ]
        """
        if not festivals:
            return []

        reference_date = cls.normalize_date(date)

        upcoming_festivals = []

        for festival in festivals:
            # Check current year and next year
            for year in (reference_date.year, reference_date.year + 1):
                try:
                    festival_date = cls.resolve_festival_date(
                        festival,
                        year,
                    )

                    if festival_date and festival_date > reference_date:
                        upcoming_festivals.append(
                            {
                                "name": festival.name,
                                "date": festival_date,
                                "days": (festival_date - reference_date).days,
                            }
                        )
                        break

                except ValueError:
                    log.debug(
                        "Skipping invalid festival: %s (%s)",
                        festival.name,
                        year,
                    )

        return sorted(
            upcoming_festivals,
            key=lambda item: item["days"],
        )

    @staticmethod
    def get_year_progress(
        now: datetime.datetime | None = None,
    ) -> float:
        """
        Calculate year progress percentage.

        Returns:
            Float between 0.00 and 100.00
        """
        current_time = now or datetime.datetime.now()

        year_start = datetime.datetime(
            current_time.year,
            1,
            1,
            tzinfo=current_time.tzinfo,
        )

        next_year_start = datetime.datetime(
            current_time.year + 1,
            1,
            1,
            tzinfo=current_time.tzinfo,
        )

        progress = (
            (current_time - year_start).total_seconds()
            / (next_year_start - year_start).total_seconds()
        ) * 100

        return round(progress, 2)
