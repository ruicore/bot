import redis

from pybot.setting import RedisConfig, config

repo = redis.Redis(**dict(config.redis))

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('secret/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()


class RedisRepository:
    def __init__(self, redis_config: RedisConfig):
        self.client = redis.Redis(**redis_config.model_dump())

    def incr(self, key: str) -> int:
        return int(self.client.incr(key))

    def get(self, key: str) -> str | None:
        value = self.client.get(key)
        return value if value else None

    def rpush(self, key: str, value: str) -> None:
        self.client.rpush(key, value)

    def lrange(self, key: str, start: int, end: int) -> list[bytes]:
        return self.client.lrange(key, start, end)


class FirebaseRepository:
    def __init__(self):
        self.collection = db.collection('users')
        self.counters = db.collection('counters')
        self.lists = db.collection('lists')

    def save_user(self, user: dict) -> None:
        name = user['name']
        self.collection.document(name).set(user)

    def get_user(self, name: str) -> dict | None:
        doc = self.collection.document(name).get()
        return doc.to_dict() if doc.exists else None

    def incr(self, key: str) -> int:
        counter_ref = self.counters.document(key)

        # 使用事务确保原子性
        @firestore.transactional
        def update_counter(transaction):
            snapshot = counter_ref.get(transaction=transaction)
            current = snapshot.get('value') if snapshot.exists else 0
            new_value = current + 1
            transaction.set(counter_ref, {'value': new_value}, merge=True)
            return new_value

        transaction = db.transaction()
        return update_counter(transaction)

    def rpush(self, key: str, value: str) -> None:
        list_ref = self.lists.document(key).collection('items')
        list_ref.add({'value': value, 'timestamp': firestore.SERVER_TIMESTAMP})

    def lrange(self, key: str, start: int, end: int) -> list[str]:
        list_ref = self.lists.document(key).collection('items')
        query = list_ref.order_by('timestamp').limit(end + 1)
        docs = query.get()

        values = [doc.to_dict()['value'] for doc in docs]
        return values[start : end + 1] if values else []


if __name__ == '__main__':
    repo = FirebaseRepository()

    # 测试用户存储和获取
    user = {'name': 'Alice', 'age': 20}
    repo.save_user(user)
    print('User:', repo.get_user('Alice'))

    # 测试计数器
    print('Counter after incr:', repo.incr('visits'))  # 1
    print('Counter after incr:', repo.incr('visits'))  # 2

    # 测试列表操作
    repo.rpush('events', 'login')
    repo.rpush('events', 'logout')
    repo.rpush('events', 'purchase')
    print('Events range [0:1]:', repo.lrange('events', 0, 1))  # ['login', 'logout']
    print('Events range [1:2]:', repo.lrange('events', 1, 2))  # ['logout', 'purchase']
