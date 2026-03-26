from croniter import croniter
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Schedule:
    scheduled_at: datetime
    is_past: bool

    @property
    def iso(self) -> str:
        return self.scheduled_at.isoformat()


# type ScheduleInfo = dict[str, str | bool | datetime]


class CronUtil:
    @staticmethod
    def get_next_time(cron: str, current_time: datetime) -> datetime:
        """
        Get the next scheduled time for a given cron expression starting from current_time.

        Args:
            cron (str): Cron expression.
            current_time (datetime): Reference datetime (must be timezone-aware or naive consistently).

        Returns:
            datetime: Next scheduled datetime.
        """
        if current_time is None:
            raise ValueError("Current time cannot be None")
        cron_iter = croniter(cron, current_time)
        return cron_iter.get_next(datetime)

    @staticmethod
    def get_day_schedules(
        cron: str,
        current_time: datetime,
        only_future: bool = True,
    ) -> list[Schedule]:
        """
        Get all cron schedules for the day of a given time.

        Args:
            cron (str): Cron expression.
            current_time (datetime): Reference datetime for the day.
            only_future (bool, optional): If True, return only schedules after `current_time`. Defaults to True.

        Returns:
            List[Schedule]: List of Schedule objects for the day. Each object contains:
                - scheduled_at (datetime): The actual datetime of the schedule.
                - is_past (bool): True if the schedule is before `current_time`.
                - iso (str, property): ISO formatted string of the scheduled_at datetime.
        """
        if current_time is None:
            raise ValueError("Current time cannot be None")
        start_of_today = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = start_of_today + timedelta(days=1)

        iter_start = current_time if only_future else start_of_today
        cron_iter = croniter(cron, iter_start - timedelta(microseconds=1))

        schedules: list[Schedule] = []
        while True:
            next_time = cron_iter.get_next(datetime)
            if next_time >= end_of_today:
                break
            schedules.append(
                Schedule(is_past=next_time < current_time, scheduled_at=next_time)
            )

        return schedules
