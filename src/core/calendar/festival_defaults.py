from core.enums.festival_type import FestivalType
from core.calendar.models.festival import Festival

DEFAULT_FESTIVALS: tuple[Festival, ...] = (
    Festival(
        name="元旦节", type=FestivalType.FIXED, month=1, day=1, is_public_holiday=True
    ),
    Festival(
        name="春节", type=FestivalType.LUNAR, month=1, day=1, is_public_holiday=True
    ),
    Festival(name="情人节", type=FestivalType.FIXED, month=2, day=14),
    Festival(
        name="清明节",
        type=FestivalType.TERM,
        nth=6,
        term_name="清明",
        is_public_holiday=True,
    ),
    Festival(
        name="劳动节", type=FestivalType.FIXED, month=5, day=1, is_public_holiday=True
    ),
    Festival(name="母亲节", type=FestivalType.WEEK, month=5, nth=2, weekday=6),
    Festival(
        name="端午节", type=FestivalType.LUNAR, month=5, day=5, is_public_holiday=True
    ),
    Festival(name="父亲节", type=FestivalType.WEEK, month=6, nth=3, weekday=6),
    Festival(name="七夕节", type=FestivalType.LUNAR, month=7, day=7),
    Festival(
        name="中秋节", type=FestivalType.LUNAR, month=8, day=15, is_public_holiday=True
    ),
    Festival(
        name="国庆节", type=FestivalType.FIXED, month=10, day=1, is_public_holiday=True
    ),
    Festival(name="黑色星期五", type=FestivalType.WEEK, month=11, nth=4, weekday=4),
    Festival(name="圣诞节", type=FestivalType.FIXED, month=12, day=25),
)
