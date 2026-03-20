import datetime
import requests
from typing import Any
from chinese_calendar import is_workday, get_holiday_detail
from utils.logger import setup_logger

log = setup_logger("Holiday")


class HolidayUtil:
    WEEKDAY_NAME_CN = {
        "Monday": "周一",
        "Tuesday": "周二",
        "Wednesday": "周三",
        "Thursday": "周四",
        "Friday": "周五",
        "Saturday": "周六",
        "Sunday": "周日",
    }

    API_URL = "https://apis.tianapi.com/jiejiari/index"

    @staticmethod
    def get_day_status(
        date_value: datetime.date | datetime.datetime | None = None,
    ) -> dict[str, Any]:
        """
        Get the workday/holiday status for a given date.

        Args:
            date_value: Target date. If None, today's date will be used.
                        Accepts both date and datetime objects.

        Returns:
            DayStatus: A dictionary containing:
                - is_workday: Whether the date is a workday
                - is_holiday: Whether the date is a public holiday
                - holiday_name: Name of the holiday (if applicable)
                - is_weekend: Whether the date falls on a weekend
        """
        target_date = date_value or datetime.date.today()

        # Normalize datetime to date
        if isinstance(target_date, datetime.datetime):
            target_date = target_date.date()

        is_workday_flag = is_workday(target_date)
        is_holiday_flag, holiday_name = get_holiday_detail(target_date)
        return {
            "date": target_date,
            "is_workday": is_workday_flag,
            "is_holiday": is_holiday_flag,
            "holiday_name": holiday_name,
            "is_weekend": target_date.weekday() >= 5,
            "weekday_cn": HolidayUtil.get_weekday_cn(target_date),
        }

    @staticmethod
    def get_weekday_cn(date_value: datetime.datetime | datetime.date) -> str:
        # e.g. 'Monday'
        weekday_en = date_value.strftime("%A")
        return HolidayUtil.WEEKDAY_NAME_CN[weekday_en]

    @staticmethod
    def fetch_day_status_from_api(
        api_key: str, date_value: datetime.date | datetime.datetime | None = None
    ) -> dict[str, Any]:
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
        if not items:
            return {
                "date": target_date,
                "is_workday": target_date.weekday() < 5,
                "is_holiday": False,
                "holiday_name": None,
                "is_weekend": target_date.weekday() >= 5,
            }

        item = items[0]

        is_holiday_flag = item.get("isnotwork") == 1
        holiday_name = item.get("name") if is_holiday_flag else None

        return {
            "date": target_date,
            "is_workday": not is_holiday_flag,
            "is_holiday": is_holiday_flag,
            "holiday_name": holiday_name,
            "is_weekend": target_date.weekday() >= 5,
        }
