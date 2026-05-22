import datetime
import requests
from typing import Any
from chinese_calendar import is_workday, get_holiday_detail
from core.calendar.models.day_status import DayStatus
from utils.calendar_util import CalendarUtil
from utils.logger import setup_logger

log = setup_logger("Holiday")


class HolidayUtil:

    WEEKDAY_NUMBER_CN = {
        "Monday": "一",
        "Tuesday": "二",
        "Wednesday": "三",
        "Thursday": "四",
        "Friday": "五",
        "Saturday": "六",
        "Sunday": "日",
    }

    API_URL = "https://apis.tianapi.com/jiejiari/index"

    @staticmethod
    def get_day_status(
        date_value: datetime.date | datetime.datetime | None = None,
    ) -> DayStatus:
        """
        Get status information for a given day.
        """

        target_date = date_value or datetime.date.today()

        if isinstance(target_date, datetime.datetime):
            target_date = target_date.date()

        is_holiday_flag, holiday_name = get_holiday_detail(target_date)
        
        festival_names = CalendarUtil.get_festival_names(target_date)
        return DayStatus(
            date=target_date,
            is_workday=is_workday(target_date),
            is_holiday=is_holiday_flag,
            holiday_name=holiday_name,
            festival_names=festival_names,
            is_weekend=target_date.weekday() >= 5,
            weekday_cn_short=HolidayUtil.get_weekday_cn_short(target_date),
        )

    @staticmethod
    def get_weekday_cn_short(date_value: datetime.datetime | datetime.date) -> str:
        # e.g. 'Monday'
        weekday_en = date_value.strftime("%A")
        return HolidayUtil.WEEKDAY_NUMBER_CN[weekday_en]

    @staticmethod
    def fetch_day_status_from_api(
        api_key: str, date_value: datetime.date | datetime.datetime | None = None
    ) -> DayStatus:
        """
        Fetch the day status from TianAPI (sync version using requests).
        """
        if not api_key:
            raise ValueError("API key must be provided")
        target_date = date_value or datetime.date.today()
        if isinstance(target_date, datetime.datetime):
            target_date = target_date.date()
        date_str = target_date.strftime("%Y-%m-%d")

        payload = {
            "key": api_key,
            "date": date_str,
        }

        try:
            response = requests.post(
                HolidayUtil.API_URL,
                data=payload,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5,
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()

        except requests.RequestException as e:
            raise RuntimeError(f"Holiday API request failed: {e}") from e

        # Validate response
        if data.get("code") != 200 or "result" not in data:
            raise ValueError(f"Invalid API response: {data}")
        log.info(f"API response: {data}")
        items = data["result"].get("list", [])
        festival_names = CalendarUtil.get_festival_names(target_date)
        if not items:
            return DayStatus(
                date=target_date,
                weekday=target_date.weekday(),
                weekday_cn_short=HolidayUtil.get_weekday_cn_short(target_date),
                is_weekend=target_date.weekday() >= 5,
                is_workday=target_date.weekday() < 5,
                is_holiday=False,
                holiday_name=None,
                festival_names=festival_names,
            )

        item = items[0]

        is_holiday_flag = item.get("isnotwork") == 1
        holiday_name = item.get("name") if is_holiday_flag else None

        return DayStatus(
            date=target_date,
            weekday=target_date.weekday(),
            weekday_cn_short=HolidayUtil.get_weekday_cn_short(target_date),
            is_weekend=target_date.weekday() >= 5,
            is_workday=not is_holiday_flag,
            is_holiday=is_holiday_flag,
            holiday_name=holiday_name,
            festival_names=festival_names,
        )
