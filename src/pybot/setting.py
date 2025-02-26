import configparser

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

    @classmethod
    def from_config(cls, file: str = '.ini') -> 'Config':
        parser = configparser.ConfigParser()
        parser.read(file)
        return cls(**{s.lower(): dict(parser.items(s)) for s in parser.sections()})  # type:ignore


config = Config.from_config()
