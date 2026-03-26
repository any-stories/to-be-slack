import datetime
from dataclasses import dataclass
from typing import Any, Literal
from config import Settings
from utils.calendar_util import CalendarUtil
from utils.holiday_util import HolidayUtil
from utils.one_sentence_util import OneSentenceUtil


@dataclass
class YearStats:
    progress: float

    BAR_STYLES = {
        "line": ("━", "─"),
        "block": ("█", "░"),
        "solid": ("█", "▓"),
        "empty": ("█", " "),
    }

    def _calculate_bar(
        self, length: int, fill_char: str, empty_char: str
    ) -> tuple[str, str]:
        ratio = max(0.0, min(float(self.progress), 100.0)) / 100
        filled_count = round(ratio * length)
        empty_count = length - filled_count
        return fill_char * filled_count, empty_char * empty_count

    def render_bar(
        self,
        length: int = 10,
        style: Literal["line", "block", "solid", "empty"] = "block",
    ) -> str:
        chars = self.BAR_STYLES.get(style, self.BAR_STYLES["empty"])
        filled, empty = self._calculate_bar(length, *chars)
        return f"{filled}{empty} {self.progress}%"

    def render_wecom_html(
        self, length: int = 10, fill_char: str = "─", empty_char: str = "─"
    ) -> str:
        filled_str, empty_str = self._calculate_bar(length, fill_char, empty_char)

        filled_bar = self.apply_color(filled_str, "warning")
        empty_bar = self.apply_color(empty_str, "comment")

        num_color = (
            "info"
            if self.progress < 30
            else "warning" if self.progress < 85 else "comment"
        )
        percent_text = self.apply_color(f"{self.progress:.2f}%", num_color)

        return f"{filled_bar}{empty_bar} {percent_text}"

    @staticmethod
    def apply_color(text: Any, color: str) -> str:
        return f'<font color="{color}">{text}</font>'


class MessageContextBuilder:

    WEEKDAY_NAME_CN = {
        "Monday": "周一",
        "Tuesday": "周二",
        "Wednesday": "周三",
        "Thursday": "周四",
        "Friday": "周五",
        "Saturday": "周六",
        "Sunday": "周日",
    }

    @staticmethod
    def get_greeting_text(hour: int) -> str:
        GREETING_TEXTS = {
            (0, 5): "还不滚去睡觉?",
            (5, 11): "上午好",
            (11, 13): "中午好",
            (13, 19): "下午好",
            (19, 24): "晚上好",
        }
        for (start, end), text in GREETING_TEXTS.items():
            if start <= hour < end:
                return text
        return ""

    @staticmethod
    def get_weekday_cn(date_value: datetime.datetime | datetime.date) -> str:
        # e.g. 'Monday'
        weekday_en = date_value.strftime("%A")
        return MessageContextBuilder.WEEKDAY_NAME_CN[weekday_en]

    @staticmethod
    def get_workweek_status(today: datetime.date) -> dict:
        friday = CalendarUtil.get_friday_of_week(today)

        # tomorrow info
        tomorrow_date = today + datetime.timedelta(days=1)
        tomorrow_status = HolidayUtil.get_day_status(tomorrow_date)

        status = {
            "friday": {
                "date": friday,
                "days_until": max((friday - today).days, 0),
                "is_today": today == friday,
            },
            "tomorrow": {
                "date": tomorrow_date,
                "is_workday": tomorrow_status.get("is_workday", True),
            },
            "next_friday": None,
        }

        if today > friday:
            next_friday = friday + datetime.timedelta(days=7)
            status["next_friday"] = {
                "date": next_friday,
                "days_until": (next_friday - today).days,
            }

        return status

    @staticmethod
    def build(
        today_status: dict[str, Any],
        business_time: datetime.datetime,
        settings: Settings,
    ) -> dict:
        today = business_time.date()
        context = {
            "today_status": today_status,
            "lunar_date": CalendarUtil.get_lunar_date(today),
            "greeting": MessageContextBuilder.get_greeting_text(business_time.hour),
            "header_text": "工作再累 一定不要忘记摸鱼哦 有事没事起身去茶水间去厕所去廊道走走 别老在工位上坐着 钱是老板的 但命是自己的",
            "year_progress_status": YearStats(
                CalendarUtil.get_year_progress(business_time)
            ),
            "workweek_status": MessageContextBuilder.get_workweek_status(today),
            "festivals": CalendarUtil.get_upcoming_festivals(today, settings.festivals),
            "footer_text": "上班是帮老板赚钱 摸鱼是赚老板的钱 最后祝愿天下所有摸鱼人 都能愉快的渡过每一天~",
        }
        context["one_sentence"] = (
            OneSentenceUtil.fetch_hitokoto() if settings.enable_random_sentence else {}
        )
        return context
