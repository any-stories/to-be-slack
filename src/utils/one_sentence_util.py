import requests
from typing import Any

class OneSentenceUtil:
    
    HITOKOTO_API_URL = "https://v1.hitokoto.cn/"

    @staticmethod
    def fetch_hitokoto(
        categories: str | list[str] | None = None,
        charset: str = "utf-8",
        min_length: int = 0,
        max_length: int = 30,
        timeout: int = 3
    ) -> dict[str, str]:
        """
        Fetch a one-line quote from hitokoto API.

        Args:
            categories: category codes as string (e.g., "d") or list (e.g., ["a", "c"])
            charset: character set, default 'utf-8'
            min_length: minimum sentence length (inclusive)
            max_length: maximum sentence length (inclusive)
            timeout: request timeout in seconds

        Returns:
            Dict with keys:
                - 'content': the quote
                - 'source': source of the quote
                - 'author': author if provided
        """
        if categories is None:
            categories = ['d', 'e', 'f', 'h', 'j']
        elif isinstance(categories, str):
            categories = [categories]

        params: dict[str, Any] = {
            "c": categories,
            "encode": 'json',
            "charset": charset,
            "min_length": min_length,
            "max_length": max_length,
        }

        try:
            r = requests.get(OneSentenceUtil.HITOKOTO_API_URL, params=params, timeout=timeout)
            r.raise_for_status()
            data: dict[str, Any] = r.json()
            return {
                "content": data.get("hitokoto", ""),
                "source": data.get("from", ""),
                "author": data.get("from_who", ""),
            }
        except requests.RequestException as e:
            # RuntimeError(f"Failed to fetch one-sentence quote: {e}") from e
            return {}