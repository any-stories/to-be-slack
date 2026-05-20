from dataclasses import dataclass
import datetime
import random
from typing import Sequence, TypeVar

from core.enums import DayPeriod

from core.message.models import MessageContext

from core.message.components import MessageComponent, MessageScene, MessageTone

T = TypeVar("T", bound=MessageComponent)


@dataclass(slots=True)
class MessagePack:

    scenes: list[MessageScene]

    greetings: dict[DayPeriod, list[str]]

    tones: list[MessageTone]

    def get_greeting(self, dt: datetime.datetime) -> str:

        period = DayPeriod.from_hour(dt.hour)

        greetings = self.greetings.get(
            period,
            [],
        )

        if not greetings:
            return ""

        return random.choice(greetings)

    def _weighted_pick(self, items: Sequence[T], context: MessageContext) -> T | None:
        if not items:
            return None

        valid_items: list[T] = []
        weights: list[float] = []

        # 过滤和权重提取
        for item in items:
            w = item.score(context)
            if w > 0:
                valid_items.append(item)
                weights.append(w)

        if not valid_items:
            return None

        return random.choices(valid_items, weights=weights, k=1)[0]

    def get_scene(self, context: MessageContext) -> str:
        scene = self._weighted_pick(self.scenes, context)
        return scene.text if scene else ""

    def get_tone(self, context: MessageContext) -> MessageTone:
        tone = self._weighted_pick(self.tones, context)
        return tone if tone else MessageTone(header="", footer="")
