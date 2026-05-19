from dataclasses import dataclass
import datetime
import random

from core.message.context import MessageContext

from core.style.message_scene import MessageScene
from core.style.message_tone import MessageTone
from core.style.day_period import DayPeriod


@dataclass(slots=True)
class MessagePack:

    scenes: list[MessageScene]

    greetings: dict[DayPeriod, list[str]]

    tones: list[MessageTone]

    def get_scene(self, context: MessageContext) -> str:

        available_scenes = [
            scene for scene in self.scenes if scene.is_available(context)
        ]

        if not available_scenes:
            return ""

        return random.choice(available_scenes).text

    def get_greeting(self, dt: datetime.datetime) -> str:

        period = DayPeriod.from_hour(dt.hour)

        greetings = self.greetings.get(
            period,
            [],
        )

        if not greetings:
            return ""

        return random.choice(greetings)

    def get_tone(self, context: MessageContext) -> MessageTone:

        available_tones = [tone for tone in self.tones if tone.is_available(context)]

        if not available_tones:

            return MessageTone(
                header="",
                footer="",
            )

        return random.choice(available_tones)
