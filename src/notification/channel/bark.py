import requests
from typing import Any
from core.base_result import Result
from utils.logger import setup_logger

log = setup_logger("notifier")


class BarkMessage:
    def __init__(
        self,
        body: str,
        title: str = "Notification",
        badge: int | None = None,
        sound: str | None = None,
        icon: str | None = None,
        group: str | None = None,
        url: str | None = None,
        level: str | None = None,
    ):
        self.body = body
        self.title = title
        self.badge = badge
        self.sound = sound
        self.icon = icon
        self.group = group
        self.url = url
        self.level = level

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class BarkApp:
    """
    https://bark.day.app/
    """
    DEFAULT_WEBHOOK_BASE: str = "https://api.day.app"

    def __init__(self, key: str):
        if not key:
            raise ValueError("Bark requires non-empty key")
        self.api_url: str = f"{self.DEFAULT_WEBHOOK_BASE.rstrip('/')}/{key}"

    def send(self, message: BarkMessage | str) -> Result[None]:
        match message:
            case str():
                msg_obj = BarkMessage(body=message)
            case BarkMessage():
                msg_obj = message
            case _:
                err = f"Invalid type: {type(message)}. Use BarkMessage or str."
                log.error(err)
                return Result.fail(msg=err)

        payload = msg_obj.to_dict()

        try:
            r = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json; charset=utf-8"},
                timeout=10,
            )
            r.raise_for_status()

            body = r.json()
            if body.get("code") == 200:
                return Result.ok(msg="Bark notification sent successfully")

            return Result.fail(msg=f"Bark API Error: {body.get('message')}")

        except requests.exceptions.RequestException as e:
            return Result.fail(msg=f"Network error: {e}")
        except Exception:
            log.exception("Bark unexpected error")
            return Result.fail(msg="Unexpected error")
