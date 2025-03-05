import configparser
import os
from typing import Any, ClassVar

from pydantic import BaseModel


class Telegram(BaseModel):
    access_token: str


class ChatGPT(BaseModel):
    basicurl: str
    modelname: str
    apiversion: str
    access_token: str


class Config(BaseModel):
    telegram: Telegram
    redis: dict[str, str | bool]
    chatgpt: ChatGPT

    SECRETS: ClassVar[list[str]] = ['TELEGRAM_ACCESS_TOKEN', 'REDIS_PASSWORD', 'CHATGPT_ACCESS_TOKEN']

    @classmethod
    def from_config(cls, file: str = '.ini') -> 'Config':
        parser = configparser.ConfigParser()
        parser.read(file)
        return cls(
            **cls.merge_secrets(
                {s.lower(): dict(parser.items(s)) for s in parser.sections()},
            ),
        )

    @classmethod
    def merge_secrets(cls, data: dict[str, Any]) -> dict[str, Any]:
        for key in cls.SECRETS:
            pre, post = key.lower().split('_', 1)
            data.setdefault(pre, {})[post] = os.environ[key]

        return data


config = Config.from_config()

if __name__ == '__main__':
    pass
