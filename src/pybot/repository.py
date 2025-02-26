import redis

from pybot.setting import config

repo = redis.Redis(**config.redis)  # type:ignore
