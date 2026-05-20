from dataclasses import dataclass

from core.message.components.component import MessageComponent


@dataclass(slots=True, kw_only=True)
class MessageTone(MessageComponent):

    header: str

    footer: str
