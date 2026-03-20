import re
from abc import ABC, abstractmethod
from typing import Any

import requests
from core.base_result import Result
from utils.logger import setup_logger

type TGPayload = dict[str, Any]

log = setup_logger("notifier")


class TGMessage(ABC):
    @abstractmethod
    def to_payload(self) -> TGPayload:
        pass

    @staticmethod
    def escape_md_v2(text: str) -> str:
        specials = r"_*[]()~`>#+-=|{}.!"
        return re.sub(f"([{re.escape(specials)}])", r"\\\1", text)


class TGText(TGMessage):
    def __init__(
        self, text: str, parse_mode: str = "MarkdownV2", disable_preview: bool = True
    ):
        self.text = text
        self.parse_mode = parse_mode
        self.disable_preview = disable_preview

    def to_payload(self) -> TGPayload:
        content = (
            self.escape_md_v2(self.text)
            if self.parse_mode == "MarkdownV2"
            else self.text
        )
        return {
            "text": content,
            "parse_mode": self.parse_mode,
            "disable_web_page_preview": self.disable_preview,
        }


class TGButton(TGMessage):
    def __init__(
        self, text: str, btn_text: str, btn_url: str, parse_mode: str = "HTML"
    ):
        self.text = text
        self.btn_text = btn_text
        self.btn_url = btn_url
        self.parse_mode = parse_mode

    def to_payload(self) -> TGPayload:
        return {
            "text": self.text,
            "parse_mode": self.parse_mode,
            "reply_markup": {
                "inline_keyboard": [[{"text": self.btn_text, "url": self.btn_url}]]
            },
        }


type TGInput = TGMessage | str | dict[str, Any]


class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        if not token or not chat_id:
            raise ValueError("TelegramBot token and chat_id cannot be empty")
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send(self, message: TGInput) -> Result[None]:
        match message:
            case TGMessage() as msg_obj:
                payload = msg_obj.to_payload()
            case str() as raw_text:
                payload = TGText(text=raw_text).to_payload()
            case dict() as raw_dict:
                payload = raw_dict
            case _:
                err = f"Unsupported message type: {type(message)}"
                log.error(err)
                return Result.fail(msg=err)

        payload["chat_id"] = self.chat_id

        return self._post_json(payload)

    def _post_json(self, payload: dict[str, Any]) -> Result[None]:
        try:
            r = requests.post(self.base_url, json=payload, timeout=10)
            r.raise_for_status()
            body = r.json()

            if body.get("ok"):
                return Result.ok(msg="Telegram notification sent successfully")

            err_desc = body.get("description", "Unknown error")
            err_code = body.get("error_code")
            msg = f"TG API Error {err_code}: {err_desc}"
            log.error(msg)
            return Result.fail(msg=msg)

        except requests.exceptions.RequestException as e:
            return Result.fail(msg=f"Network error: {str(e)}")
        except Exception:
            log.exception("Telegram unexpected exception")
            return Result.fail(msg="Internal server error")
