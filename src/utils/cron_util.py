from croniter import croniter
from datetime import datetime, timezone, timedelta
from typing import Any


class CronUtil:
    @staticmethod
    def get_next_time(
        cron: str, current_time: datetime | None = None, tz: timezone = timezone.utc
    ) -> datetime:
        if current_time is None:
            current_time = datetime.now(tz)
        else:
            current_time = current_time.astimezone(tz)

        cron_iter = croniter(cron, current_time)
        return cron_iter.get_next(datetime)

    @staticmethod
    def get_day_schedules(
        cron: str,
        current_time: datetime | None = None,
        tz: timezone = timezone.utc,
        only_future: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Get all cron schedules for the day of a given time in a specific timezone.

        Args:
            cron (str): The cron expression to evaluate.
            current_time (datetime | None, optional): Reference time to determine the day. 
                Defaults to current time in the specified timezone if None.
            tz (timezone, optional): Timezone in which the cron should be evaluated. 
                Defaults to UTC.
            only_future (bool, optional): If True, return only schedules after `current_time`. 
                Defaults to True.

        Returns:
            list[dict[str, Any]]: A list of dictionaries representing each schedule. Each dict contains:
                - "iso" (str): ISO formatted datetime string of the schedule.
                - "is_past" (bool): True if the schedule is before `current_time`.
                - "datetime_obj" (datetime): The actual tz-aware datetime object.
        """
        if current_time is None:
            current_time = datetime.now(tz)
        else:
            current_time = current_time.astimezone(tz)

        start_of_today = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = start_of_today + timedelta(days=1)

        cron_iter = croniter(cron, start_of_today - timedelta(seconds=1))

        schedules = []
        while True:
            next_date = cron_iter.get_next(datetime)
            if next_date >= end_of_today:
                break

            is_past = next_date < current_time
            if only_future and is_past:
                continue

            schedules.append(
                {
                    "iso": next_date.isoformat(),
                    "is_past": is_past,
                    "datetime_obj": next_date,
                }
            )

        return schedules
