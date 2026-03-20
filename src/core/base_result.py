from dataclasses import dataclass
from typing import TypeVar, Generic, Any

T = TypeVar("T")

@dataclass
class Result(Generic[T]):
    success: bool
    msg: str = ""
    data: T | None = None

    @classmethod
    def ok(cls, data: T | None = None, msg: str = "success") -> "Result[T]":
        return cls(success=True, msg=msg, data=data)

    @classmethod
    def fail(cls, msg: str = "failed", data: Any | None = None) -> "Result[Any]":
        return cls(success=False, msg=msg, data=data)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "msg": self.msg,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Result[Any]":
        return cls(
            success=d.get("success", False),
            msg=d.get("msg", ""),
            data=d.get("data")
        )