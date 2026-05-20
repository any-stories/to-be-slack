from dataclasses import dataclass

from core.message.components.component import MessageComponent


@dataclass(slots=True, kw_only=True)
class MessageScene(MessageComponent):
    text: str
