import redis
from setting import RedisConfig, config

repo = redis.Redis(**dict(config.redis))



class RedisRepository:
    def __init__(self, redis_config: RedisConfig):
        self.client = redis.Redis(**redis_config.model_dump())

    def incr(self, key: str) -> int:
        return int(self.client.incr(key))

    def get(self, key: str) -> str | None:
        value = self.client.get(key)
        return value.decode('utf-8') if value else None

    def rpush(self, key: str, value: str) -> None:
        self.client.rpush(key, value)

    def lrange(self, key: str, start: int, end: int) -> list[bytes]:
        """Get a range of values from a Redis list."""
        return self.client.lrange(key, start, end)
