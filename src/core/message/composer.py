import datetime
import random

from core.enums import MessageStyle, FestivalPushMode

from core.message.models import MessagePack, YearStats, MessageContext
from core.message.renderer import MessageRenderer

from core.message.styles.registry import STYLE_REGISTRY

from core.calendar.models import (
    DayStatus,
    Festival,
    WeekendStatus,
    TomorrowStatus,
    FridayStatus,
    NextFridayStatus,
)

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

        friday = CalendarUtil.get_week_friday(today)

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
    def filter_festivals(
        festivals: tuple[Festival, ...],
        mode: FestivalPushMode,
    ) -> tuple[Festival, ...]:
        enabled = tuple(festival for festival in festivals if festival.enabled)
        if mode == FestivalPushMode.RANDOM:
            mode = random.choice(
                [
                    FestivalPushMode.ALL,
                    FestivalPushMode.PUBLIC_HOLIDAYS_ONLY,
                ]
            )
        if mode == FestivalPushMode.ALL:
            return enabled
        if mode == FestivalPushMode.PUBLIC_HOLIDAYS_ONLY:
            return tuple(festival for festival in enabled if festival.is_public_holiday)
        return enabled

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

        filtered_festivals = MessageComposer.filter_festivals(
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
