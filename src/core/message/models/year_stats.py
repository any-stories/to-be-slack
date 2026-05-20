from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class YearStats:
    progress: float

    BAR_STYLES = {
        "line": ("━", "─"),
        "block": ("█", "░"),
        "solid": ("█", "▓"),
        "empty": ("█", " "),
    }

    def _calculate_bar(
        self, length: int, fill_char: str, empty_char: str
    ) -> tuple[str, str]:
        ratio = max(0.0, min(float(self.progress), 100.0)) / 100
        filled_count = round(ratio * length)
        empty_count = length - filled_count
        return fill_char * filled_count, empty_char * empty_count

    def render_bar(
        self,
        length: int = 10,
        style: Literal["line", "block", "solid", "empty"] = "block",
    ) -> str:
        chars = self.BAR_STYLES.get(style, self.BAR_STYLES["empty"])
        filled, empty = self._calculate_bar(length, *chars)
        return f"{filled}{empty} {self.progress}%"

    def render_wecom_html(
        self, length: int = 10, fill_char: str = "─", empty_char: str = "─"
    ) -> str:
        filled_str, empty_str = self._calculate_bar(length, fill_char, empty_char)

        filled_bar = self.apply_color(filled_str, "warning")
        empty_bar = self.apply_color(empty_str, "comment")

        num_color = (
            "info"
            if self.progress < 30
            else "warning" if self.progress < 85 else "comment"
        )
        percent_text = self.apply_color(f"{self.progress:.2f}%", num_color)

        return f"{filled_bar}{empty_bar} {percent_text}"

    @staticmethod
    def apply_color(text: Any, color: str) -> str:
        return f'<font color="{color}">{text}</font>'
