import os
import json
import datetime
from dataclasses import dataclass, field
from enum import StrEnum

from dotenv import load_dotenv

from utils.logger import log

from core.style.message_style import MessageStyle

from core.festival import (
    Festival,
    FestivalPushMode,
    DEFAULT_FESTIVALS,
)

# current_dir = Path(__file__).parent
# dotenv_path = current_dir.parent / ".env"
load_dotenv()


class PushChannel(StrEnum):
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
    festival_push_mode: FestivalPushMode = FestivalPushMode.ALL

    message_style: MessageStyle = MessageStyle.DEFAULT

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
            festival_push_mode=FestivalPushMode.from_value(
                cfg.get("festival_push_mode")
            ),
            message_style=MessageStyle.from_value(cfg.get("message_style")),
        )


settings = Settings.from_env()
