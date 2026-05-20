import datetime
import calendar
from borax.calendars.lunardate import LunarDate, TermUtils
from borax.calendars.festivals2 import FestivalLibrary, SolarFestival, LunarFestival

from core.enums import FestivalType
from core.calendar.models import Festival

from utils.logger import setup_logger

log = setup_logger("calendar")


class CalendarUtil:

    _festival_lib = None

    @classmethod
    def _get_festival_lib(cls) -> FestivalLibrary:
        if cls._festival_lib is None:
            cls._festival_lib = FestivalLibrary.load_builtin()
            valentine_months = {
                1: "日记情人节",
                2: "传统情人节",
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

            monthly_valentines = [
                SolarFestival(month=m, day=14, name=name)
                for m, name in valentine_months.items()
            ]
            custom_festivals = [
                SolarFestival(month=10, day=24, name="程序员节"),
                SolarFestival(month=5, day=20, name="网络情人节"),
                SolarFestival(month=6, day=18, name="电商年中大促"),
                SolarFestival(month=11, day=11, name="双十一"),
                SolarFestival(month=12, day=12, name="双十二"),
                SolarFestival(month=3, day=7, name="女生节"),
                SolarFestival(month=11, day=11, name="光棍节"),
                LunarFestival(month=12, day=23, name="北小年"),
                LunarFestival(month=12, day=24, name="南小年"),
            ]
            cls._festival_lib.extend(monthly_valentines + custom_festivals)
        return cls._festival_lib

    @staticmethod
    def normalize_date(
        date_value: datetime.date | datetime.datetime | str | None = None,
    ) -> datetime.date:
        """Normalize input to a datetime.date object."""
        if date_value is None:
            return datetime.date.today()
        if isinstance(date_value, datetime.datetime):
            return date_value.date()
        if isinstance(date_value, datetime.date):
            return date_value
        if isinstance(date_value, str):
            try:
                return datetime.datetime.strptime(date_value, "%Y-%m-%d").date()
            except ValueError as e:
                raise ValueError(f"Invalid date string format: {date_value}") from e
        raise TypeError("date_value must be date, datetime, or 'YYYY-MM-DD' string")

    @staticmethod
    def is_weekday(
        date_value: datetime.date | datetime.datetime | str, weekday: int
    ) -> bool:
        """
        Check if the given date matches a specific weekday.

        Args:
            date_value: date to check
            weekday: integer, 0=Monday ... 6=Sunday. If None, checks if weekday (Mon-Fri)

        Returns:
            True if it matches the weekday (or is Mon-Fri if weekday=None)
        """
        target = CalendarUtil.normalize_date(date_value)
        if not 0 <= weekday <= 6:
            raise ValueError("weekday must be between 0 (Monday) and 6 (Sunday)")
        return target.weekday() == weekday

    @staticmethod
    def is_friday(date_value: datetime.date | datetime.datetime | str) -> bool:
        """
        Check if the given date is Friday (0=Mon ... 4=Fri)
        """
        return CalendarUtil.is_weekday(date_value, weekday=4)

    @staticmethod
    def get_friday_of_week(
        date_value: datetime.date | datetime.datetime | None = None,
    ) -> datetime.date:
        """Get the Friday of the week containing the given date."""
        target = CalendarUtil.normalize_date(date_value)
        days_ahead = 4 - target.weekday()
        return target + datetime.timedelta(days=days_ahead)

    @staticmethod
    def get_nth_weekday(year: int, month: int, nth: int, weekday: int) -> datetime.date:
        """Get the date of the nth weekday in a specific month."""
        cal = calendar.Calendar(firstweekday=0)
        month_days = [
            day
            for week in cal.monthdays2calendar(year, month)
            for day, wd in week
            if day != 0 and wd == weekday
        ]
        if nth - 1 >= len(month_days):
            raise ValueError(f"No {nth}-th weekday {weekday} in {year}-{month}")
        return datetime.date(year, month, month_days[nth - 1])

    @staticmethod
    def get_lunar_date(
        date_value: datetime.date | datetime.datetime | str | None = None,
    ) -> LunarDate:
        target = CalendarUtil.normalize_date(date_value)
        return LunarDate.from_solar(target)

    @staticmethod
    def get_all_festival_names(target_date: datetime.date) -> list[str]:
        names = []
        try:

            lib = CalendarUtil._get_festival_lib()
            names.extend(lib.get_festival_names(target_date))

            # 节气
            # lunar_date = LunarDate.from_solar_date(target_date)
        except Exception as e:
            log.error(f"Failed to get festival names for {target_date}: {e}")

        return names

    @classmethod
    def get_upcoming_festivals(
        cls,
        date_value: datetime.date | datetime.datetime | str | None = None,
        festivals: tuple[Festival, ...] = None,
    ) -> list[dict[str, str | int]]:
        """
        Get a list of upcoming festivals after the given date.

        Returns:
            List of dicts with keys: 'name', 'date', 'days'
        """
        if not festivals:
            return []

        reference = cls.normalize_date(date_value)

        results: list[dict[str, str | int]] = []
        seen_names: set[str] = set()
        current_year = reference.year

        # check next year as well
        for year in range(current_year, current_year + 2):
            if len(results) >= len(festivals):
                break

            for festival in festivals:
                if festival.name in seen_names:
                    continue

                try:
                    target: datetime.date | None = None
                    match festival:
                        case Festival(type=FestivalType.FIXED, month=month, day=day):
                            target = datetime.date(year, month, day)
                        case Festival(type=FestivalType.LUNAR, month=month, day=day):
                            target = LunarDate(year, month, day).to_solar_date()
                        case Festival(
                            type=FestivalType.WEEK,
                            month=month,
                            nth=nth,
                            weekday=weekday,
                        ):
                            target = cls.get_nth_weekday(year, month, nth, weekday)
                        case Festival(type=FestivalType.TERM, nth=nth, term_name=term):
                            target = TermUtils.nth_term_day(year, nth, term)

                    if target and target > reference:
                        results.append(
                            {
                                "name": str(festival.name),
                                "date": target,
                                "days": (target - reference).days,
                            }
                        )
                        seen_names.add(festival.name)
                except Exception as e:
                    log.debug(f"Skipping festival {festival.name} ({year}): {e}")

        # Sort by ascending number of days until festival
        results.sort(key=lambda x: x["days"])
        return results

    @staticmethod
    def get_year_progress(current_time: datetime.datetime | None = None) -> float:
        """
        Calculate the percentage of the year that has passed.

        Returns:
            Year progress as a float between 0.0 and 100.0
        """
        now = current_time or datetime.datetime.now()

        target_year = now.year
        year_start = datetime.datetime(target_year, 1, 1).replace(tzinfo=now.tzinfo)

        next_year_start = datetime.datetime(target_year + 1, 1, 1).replace(
            tzinfo=now.tzinfo
        )

        if now < year_start:
            return 0.0
        if now >= next_year_start:
            return 100.0
        total_seconds = (next_year_start - year_start).total_seconds()
        passed_seconds = (now - year_start).total_seconds()

        progress = (passed_seconds / total_seconds) * 100
        return round(max(0.0, min(100.0, progress)), 2)
