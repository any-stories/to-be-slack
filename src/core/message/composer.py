import datetime

from core.style import (
    YearStats,
    MessageStyle,
    MessagePack,
    STYLE_REGISTRY,
)

from core.message.context import MessageContext
from core.message.renderer import MessageRenderer

from core.message.day_status import DayStatus
from core.message.weekend_status import (
    WeekendStatus,
    TomorrowStatus,
    FridayStatus,
    NextFridayStatus,
)

from core.festival import filter_festivals

from utils.calendar_util import CalendarUtil
from utils.holiday_util import HolidayUtil
from utils.one_sentence_util import OneSentenceUtil

from config import Settings


class MessageComposer:

    _renderer = MessageRenderer()

    @staticmethod
    def resolve_style(style: MessageStyle) -> tuple[MessagePack, str]:
        return STYLE_REGISTRY.get(
            style,
            STYLE_REGISTRY[MessageStyle.DEFAULT],
        )

    @staticmethod
    def get_weekend_status(today: datetime.date) -> WeekendStatus:
        """
        Get weekend related status information.
        """

        friday = CalendarUtil.get_friday_of_week(today)

        tomorrow_date = today + datetime.timedelta(days=1)
        tomorrow_status = HolidayUtil.get_day_status(tomorrow_date)

        next_friday_status = None

        if today > friday:
            next_friday_date = friday + datetime.timedelta(days=7)

            next_friday_status = NextFridayStatus(
                date=next_friday_date,
                days_until=(next_friday_date - today).days,
            )

        return WeekendStatus(
            friday=FridayStatus(
                date=friday,
                days_until=max((friday - today).days, 0),
                is_today=today == friday,
            ),
            tomorrow=TomorrowStatus(
                date=tomorrow_date,
                is_workday=tomorrow_status.is_workday,
            ),
            next_friday=next_friday_status,
        )

    @staticmethod
    def compose(
        day_status: DayStatus,
        business_time: datetime.datetime,
        settings: Settings,
    ) -> str:

        business_date = business_time.date()

        lunar_date = CalendarUtil.get_lunar_date(business_date)

        year_progress = CalendarUtil.get_year_progress(
            business_time,
        )

        pack, template = MessageComposer.resolve_style(
            settings.message_style,
        )

        weekend_status = MessageComposer.get_weekend_status(
            business_date,
        )

        filtered_festivals = filter_festivals(
            settings.festivals,
            settings.festival_push_mode,
        )

        festivals = tuple(
            CalendarUtil.get_upcoming_festivals(
                business_date,
                filtered_festivals,
            )
        )

        one_sentence = (
            OneSentenceUtil.fetch_hitokoto()
            if settings.enable_random_sentence
            else None
        )

        context = MessageContext(
            business_time=business_time,
            day_status=day_status,
            lunar_date=lunar_date,
            year_progress=year_progress,
            weekend_status=weekend_status,
        )

        template_context = {
            # base
            "day_status": day_status,
            "lunar_date": lunar_date,
            "year_progress_status": YearStats(year_progress),
            "weekend_status": weekend_status,
            # style
            "scene": pack.get_scene(context),
            "greeting": pack.get_greeting(business_time),
            "tone": pack.get_tone(context),
            # festivals
            "festivals": festivals,
            # optional
            "one_sentence": one_sentence,
        }

        return MessageComposer._renderer.render(
            template,
            template_context,
        )
