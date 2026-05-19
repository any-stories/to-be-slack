from typing import Protocol

class LunarDateProtocol(Protocol):

    def strftime(
        self,
        fmt: str,
    ) -> str:
        ...