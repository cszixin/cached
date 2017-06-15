import redis
from .base import BaseCache
class RedisCache(BaseCache):
    def __init__(self, master="127.0.0.1:6379",salve=None,config=None):
        super(RedisCache, self).__init__(config)
        host_info = master.split(":")
        self._mconn = redis.Redis(host=host_info[0], port=int(host_info[1]))
        if not salve:
            self._sconn = self._mconn
        else:
            host_info = salve.split(":")
            self._sconn = redis.Redis(host=host_info[0], port=int(host_info[1]))


    def get(self,key):
        return self._sconn.get(key)

    def set(self,key,value):
        max_age = self.config.get('max_age',100)
        self._mconn.setex(key,value,max_age)

    def delete(self, key):
        self._mconn.delete(key)

    def clear(self):
        self._mconn.flushdb()

