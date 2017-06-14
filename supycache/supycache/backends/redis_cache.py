import redis
from .base import BaseCache
class RedisCache(BaseCache):
    def __init__(self, config=None):
        super(RedisCache, self).__init__(config)
        self._conn =  redis.Redis(host='127.0.0.1',port=6379)

    def get(self,key):
        return self._conn.get(key)

    def set(self,key,value):
        max_age = self.config.get('max_age')
        self._conn.setex(key,value,max_age)

    def delete(self, key):
        self._conn.delete(key)

    def clear(self):
        self._conn.flushdb()

