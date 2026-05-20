from core.enums.day_period import DayPeriod
from core.message.models.pack import MessagePack
from core.message.components import MessageScene, MessageTone

DEFAULT_STYLE = MessagePack(
    scenes=[
        MessageScene(
            text="又是适合摸鱼的一天",
        ),
    ],
    greetings={
        DayPeriod.LATE_NIGHT: [
            "还不睡觉？",
        ],
        DayPeriod.DAWN: [
            "天快亮了",
        ],
        DayPeriod.MORNING: [
            "上午好",
        ],
        DayPeriod.NOON: [
            "中午好",
            "午饭时间到了",
        ],
        DayPeriod.AFTERNOON: [
            "下午好",
            "离下班又近了一点",
        ],
        DayPeriod.DUSK: [
            "快到下班时间了",
        ],
        DayPeriod.EVENING: [
            "晚上好",
        ],
    },
    tones=[
        MessageTone(
            header="工作再累 一定不要忘记摸鱼哦 有事没事起身去茶水间去厕所去廊道走走 别老在工位上坐着 钱是老板的 但命是自己的",
            footer="上班是帮老板赚钱 摸鱼是赚老板的钱 最后祝愿天下所有摸鱼人 都能愉快的渡过每一天~",
        ),
    ],
)
