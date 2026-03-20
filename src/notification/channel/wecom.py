from abc import ABC, abstractmethod
from typing import Any
import requests
from core.base_result import Result
from utils.logger import setup_logger

type WeComPayload = dict[str, Any]

log = setup_logger("notifier")


class WeComMessage(ABC):
    @abstractmethod
    def to_payload(self) -> WeComPayload:
        pass


class WeComText(WeComMessage):
    def __init__(self, content: str, mentioned_list: list[str] | None = None):
        self.content = content
        self.mentioned_list = mentioned_list

    def to_payload(self) -> WeComPayload:
        return {
            "msgtype": "text",
            "text": {
                "content": self.content,
                "mentioned_list": self.mentioned_list or [],
            },
        }


class WeComMarkdown(WeComMessage):
    def __init__(self, content: str):
        self.content = content

    def to_payload(self) -> WeComPayload:
        return {"msgtype": "markdown", "markdown": {"content": self.content}}


class WeComNews(WeComMessage):
    def __init__(
        self,
        title: str,
        url: str,
        description: str | None = None,
        picurl: str | None = None,
    ):
        self.title = title
        self.url = url
        self.description = description
        self.picurl = picurl

    def to_payload(self) -> WeComPayload:
        return {
            "msgtype": "news",
            "news": {
                "articles": [
                    {
                        "title": self.title,
                        "description": self.description,
                        "url": self.url,
                        "picurl": self.picurl,
                    }
                ]
            },
        }


type WeComInput = WeComMessage | str | dict[str, Any]


class WeComBot:
    DEFAULT_WEBHOOK: str = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="

    def __init__(self, key: str):
        if not key:
            raise ValueError("WeComBot key cannot be empty")
        self.webhook_url = f"{self.DEFAULT_WEBHOOK}{key}"

    def send(self, message: WeComInput) -> Result[None]:
        match message:
            case WeComMessage() as msg_obj:
                payload = msg_obj.to_payload()
            case str() as text:
                payload = WeComText(content=text).to_payload()
            case dict() as raw_dict:
                payload = raw_dict
            case _:
                err = f"Unsupported message type: {type(message)}"
                log.error(err)
                return Result.fail(msg=err)

        return self._post_json(payload)

    def _post_json(self, payload: dict[str, Any]) -> Result[None]:
        try:
            r = requests.post(self.webhook_url, json=payload, timeout=10)
            r.raise_for_status()
            body = r.json()
            if body.get("errcode") == 0:
                return Result.ok(msg="WeCom notification sent successfully")

            msg = f"WeCom API Error: {body.get('errcode')} - {body.get('errmsg')}"
            log.error(msg)
            return Result.fail(msg=msg)

        except requests.exceptions.RequestException as e:
            return Result.fail(msg=f"Network error: {str(e)}")
        except Exception:
            log.exception("WeCom unexpected exception")
            return Result.fail(msg="Internal error")
