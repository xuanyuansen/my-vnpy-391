"""
Global setting of the trading platform.
"""

from logging import CRITICAL
from typing import Dict, Any
from tzlocal import get_localzone_name

from .utility import load_json


SETTINGS: Dict[str, Any] = {
    "font.family": "雅黑",
    "font.size": 12,

    "log.active": True,
    "log.level": CRITICAL,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "datafeed.name": "akshare",
    "datafeed.username": "13366084860",
    "datafeed.password": "417a4fe2895af56c078581f2e9a699080ebb054aceec659398c4ae88",

    "database.timezone": get_localzone_name(),
    "database.name": "mongodb",
    "database.database": "vnpy_cnstock",
    "database.host": "localhost",
    "database.port": 27017,
    "database.user": "",
    "database.password": ""
}


# Load global setting from json file.
SETTING_FILENAME: str = "vt_setting.json"
SETTINGS.update(load_json(SETTING_FILENAME))


def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length: int = len(prefix)
    settings = {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
    return settings
