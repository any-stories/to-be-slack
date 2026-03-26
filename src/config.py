import os
import json
import datetime
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv

from utils.logger import log

# current_dir = Path(__file__).parent
# dotenv_path = current_dir.parent / ".env"
load_dotenv()


@dataclass(frozen=True)
class Festival:
    name: str
    type: str
    enabled: bool = True
    month: int | None = None
    day: int | None = None
    nth: int | None = None
    weekday: int | None = None
    term_name: str | None = None


# type: fixed(公历), lunar(农历), week(某月第几个周几), term(节气)
DEFAULT_FESTIVALS: tuple[Festival, ...] = (
    Festival(name="元旦节", type="fixed", month=1, day=1),
    Festival(name="春节", type="lunar", month=1, day=1),
    Festival(name="情人节", type="fixed", month=2, day=14),
    Festival(name="清明节", type="term", nth=6, term_name="清明"),
    Festival(name="劳动节", type="fixed", month=5, day=1),
    Festival(name="母亲节", type="week", month=5, nth=2, weekday=6),
    Festival(name="端午节", type="lunar", month=5, day=5),
    Festival(name="父亲节", type="week", month=6, nth=3, weekday=6),
    Festival(name="七夕节", type="lunar", month=7, day=7),
    Festival(name="中秋节", type="lunar", month=8, day=15),
    Festival(name="国庆节", type="fixed", month=10, day=1),
    Festival(name="黑色星期五", type="week", month=11, nth=4, weekday=4),
    Festival(name="圣诞节", type="fixed", month=12, day=25),
)


class PushChannel(str, Enum):
    WECOM_BOT = "wecom_bot"
    DINGTALK = "dingtalk"


@dataclass(frozen=True)
class DoNotDisturbPeriod:
    start: datetime.time | None = None
    end: datetime.time | None = None

    @property
    def is_configured(self) -> bool:
        return self.start is not None and self.end is not None

    def is_active(self, at: datetime.datetime) -> bool:
        if not self.is_configured:
            return False
        t = at.time()
        if self.start <= self.end:
            return self.start <= t < self.end
        return t >= self.start or t < self.end


@dataclass(frozen=True)
class WecomBotConfig:
    key: str = ""


@dataclass(frozen=True)
class DingtalkConfig:
    access_token: str = ""
    secret: str = ""


@dataclass
class Settings:
    # Base
    once_per_day: bool = True
    enable_random_sentence: bool = False
    push_channel: str = "wecom_bot"

    do_not_disturb_period: DoNotDisturbPeriod | None = None

    # API
    tian_api_key: str = ""

    # Channel
    wecom_bot: WecomBotConfig = field(default_factory=WecomBotConfig)
    dingtalk: DingtalkConfig = field(default_factory=DingtalkConfig)

    # Festivals
    festivals: tuple[Festival, ...] = field(default_factory=lambda: DEFAULT_FESTIVALS)

    @classmethod
    def _parse_do_not_disturb(cls, cfg: dict) -> DoNotDisturbPeriod | None:
        dnd_cfg = cfg.get("do_not_disturb", {})
        start, end = dnd_cfg.get("start"), dnd_cfg.get("end")
        if start and end:
            try:
                return DoNotDisturbPeriod(
                    start=datetime.time.fromisoformat(start),
                    end=datetime.time.fromisoformat(end),
                )
            except ValueError:
                log.warning("Invalid DoNotDisturb time format, ignoring configuration.")
        return None

    @classmethod
    def _parse_channels(cls, cfg: dict) -> tuple[WecomBotConfig, DingtalkConfig]:
        wecom_data = cfg.get("wecom_bot", {})
        dingtalk_data = cfg.get("dingtalk", {})
        return (
            WecomBotConfig(key=wecom_data.get("key", "")),
            DingtalkConfig(
                access_token=dingtalk_data.get("access_token", ""),
                secret=dingtalk_data.get("secret", ""),
            ),
        )

    @classmethod
    def _parse_festivals(cls, cfg: dict) -> tuple[Festival, ...]:
        raw_festivals: list[dict] = cfg.get("festivals", [])
        return (
            tuple(Festival(**f) for f in raw_festivals)
            if raw_festivals
            else DEFAULT_FESTIVALS
        )

    @classmethod
    def from_env(cls) -> "Settings":
        raw_json = os.getenv("APP_CONFIG", "{}")
        try:
            cfg = json.loads(raw_json)
        except json.JSONDecodeError:
            log.warning(f"Invalid APP_CONFIG JSON, use default configuration.")
            cfg = {}

        dnd_obj = cls._parse_do_not_disturb(cfg)

        wecom_bot, dingtalk = cls._parse_channels(cfg)

        festivals = cls._parse_festivals(cfg)

        return cls(
            once_per_day=cfg.get("once_per_day", True),
            enable_random_sentence=cfg.get("enable_random_sentence", False),
            do_not_disturb_period=dnd_obj,
            push_channel=cfg.get("push_channel", "wecom_bot"),
            tian_api_key=cfg.get("tian_api_key", ""),
            wecom_bot=wecom_bot,
            dingtalk=dingtalk,
            festivals=festivals,
        )


settings = Settings.from_env()
