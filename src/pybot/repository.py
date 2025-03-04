import redis

from setting import config

repo = redis.Redis(**config.redis)  # type:ignore
