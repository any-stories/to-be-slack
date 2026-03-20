import json
import requests
from core.base_result import Result
from utils.logger import setup_logger

from abc import ABC, abstractmethod
from typing import Any

log = setup_logger("notifier")

type DingPayload = dict[str, Any]


class DingMessage(ABC):
    @abstractmethod
    def to_payload(self) -> DingPayload:
        pass


class DingText(DingMessage):
    def __init__(
        self, content: str, at_mobiles: list[str] | None = None, is_at_all: bool = False
    ):
        self.content = content
        self.at_mobiles = at_mobiles
        self.is_at_all = is_at_all

    def to_payload(self) -> DingPayload:
        return {
            "msgtype": "text",
            "text": {"content": self.content},
            "at": {"atMobiles": self.at_mobiles or [], "isAtAll": self.is_at_all},
        }


class DingMarkdown(DingMessage):
    def __init__(self, title: str, text: str):
        self.title = title
        self.text = text

    def to_payload(self) -> DingPayload:
        return {
            "msgtype": "markdown",
            "markdown": {"title": self.title, "text": self.text},
        }


class DingActionCard(DingMessage):
    def __init__(self, title: str, text: str, single_title: str, single_url: str):
        self.title = title
        self.text = text
        self.single_title = single_title
        self.single_url = single_url

    def to_payload(self) -> DingPayload:
        return {
            "msgtype": "actionCard",
            "actionCard": {
                "title": self.title,
                "text": self.text,
                "singleTitle": self.single_title,
                "singleURL": self.single_url,
            },
        }


type DingInput = DingMessage | str | dict[str, Any]


class DingTalkBot:
    DEFAULT_WEBHOOK_BASE: str = "https://oapi.dingtalk.com/robot/send?access_token="

    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("DingTalkBot requires non-empty access token")
        self.webhook: str = f"{self.DEFAULT_WEBHOOK_BASE}{access_token}"

    def send(self, message: DingInput) -> Result[None]:
        match message:
            case DingMessage() as msg_obj:
                payload = msg_obj.to_payload()
            case str() as text:
                payload = DingText(content=text).to_payload()
            case dict() as raw_dict:
                payload = raw_dict
            case _:
                err = f"Unsupported message type: {type(message)}"
                log.error(err)
                return Result.fail(msg=err)

        return self._post_json(self.webhook, payload)

    @staticmethod
    def _post_json(url: str, payload: dict[str, Any]) -> Result[None]:
        try:
            r = requests.post(url, json=payload, timeout=10)
            r.raise_for_status()
            body = r.json()

            if body.get("errcode") == 0:
                return Result.ok(msg="DingTalk notification sent successfully")

            error_msg = f"DingTalk API Error: {json.dumps(body, ensure_ascii=False)}"
            log.error(error_msg)
            return Result.fail(msg=error_msg)

        except requests.exceptions.RequestException as e:
            return Result.fail(msg=f"Network error: {str(e)}")
        except Exception:
            log.exception("DingTalk notification exception")
            return Result.fail(msg="Unexpected internal exception")
