import os
from typing import Any
from dotenv import load_dotenv

# current_dir = Path(__file__).parent
# dotenv_path = current_dir.parent / ".env"
load_dotenv()

def str2bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in ("true", "on", "1", "yes")

class Settings:

    ONCE_PER_DAY: bool = str2bool(os.getenv("ONCE_PER_DAY"), True)
    ENABLE_RANDOM_SENTENCE: bool = str2bool(os.getenv("ENABLE_RANDOM_SENTENCE"), False)
    
    PUSH_CHANNEL: str = os.getenv("PUSH_CHANNEL", "WECOM_BOT")
    WECOM_BOT_KEY:str = os.getenv("WECOM_BOT_KEY", "")
    TIAN_API_KEY: str = os.getenv("TIAN_API_KEY", "")
    
    # type: fixed(公历), lunar(农历), week(某月第几个周几), term(节气)
    FESTIVALS: list[dict[str, Any]] = [
        {'name': '元旦节', 'type': 'fixed', 'month': 1, 'day': 1, 'enabled': True},
        {'name': '春节', 'type': 'lunar', 'month': 1, 'day': 1, 'enabled': True},
        {'name': '情人节', 'type': 'fixed', 'month': 2, 'day': 14, 'enabled': True},
        {'name': '清明节', 'type': 'term', 'nth': 5, 'term_name': '清明', 'enabled': True},
        {'name': '劳动节', 'type': 'fixed', 'month': 5, 'day': 1, 'enabled': True},
        {'name': '母亲节', 'type': 'week', 'month': 5, 'nth': 2, 'weekday': 6, 'enabled': True},
        {'name': '端午节', 'type': 'lunar', 'month': 5, 'day': 5, 'enabled': True},
        {'name': '父亲节', 'type': 'week', 'month': 6, 'nth': 3, 'weekday': 6, 'enabled': True},
        {'name': '七夕节', 'type': 'lunar', 'month': 7, 'day': 7, 'enabled': True},
        {'name': '中秋节', 'type': 'lunar', 'month': 8, 'day': 15, 'enabled': True},
        {'name': '国庆节', 'type': 'fixed', 'month': 10, 'day': 1, 'enabled': True},
        {'name': '黑色星期五', 'type': 'week', 'month': 11, 'nth': 4, 'weekday': 4, 'enabled': True},
        {'name': '圣诞节', 'type': 'fixed', 'month': 12, 'day': 25, 'enabled': True},
    ]

settings = Settings()