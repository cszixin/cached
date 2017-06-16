#!/usr/bin/env python
# -*- coding:utf-8 -*-
import redis
import json
from base import BaseCache
class RedisCache(BaseCache):
    def __init__(self, master="127.0.0.1:6379",salve=None,config=None):
        # 支持redis的主从设置,写主库,读从库
        super(RedisCache, self).__init__(config)
        host_info = master.split(":")
        password = None
        if len(host_info) < 2:
            raise ValueError('redis conn[ip:port:password]')
        elif len(host_info) == 3:
            password = host_info[2]
        self._mconn = redis.Redis(host=host_info[0], port=int(host_info[1]), password=password)
        if not salve:
            self._sconn = self._mconn
        else:
            host_info = salve.split(":")
            password = None
            if len(host_info) < 2:
                raise ValueError('redis conn[ip:port:password]')
            elif len(host_info) == 3:
               password = host_info[2]
            self._sconn = redis.Redis(host=host_info[0], port=int(host_info[1]), password=password)

    def get(self,key):
        result=self._sconn.get(key)
        try:
            return json.loads(result)
        except exception as e:
            return result


    def set(self,key,value):
        # 默认key的生成时间100s
        max_age = self.config.get('max_age',100)
        if isinstance(value,dict):
            value = json.dumps(value)
        self._mconn.setex(key,value,max_age)

    def delete(self, key):
        self._mconn.delete(key)

    def clear(self):
        self._mconn.flushdb()

    @property
    def data(self):
        # 获取目前缓存的所有key:value
        def t(k,v):
            result[k] =v
        keys = self._sconn.keys()
        values = self._sconn.mget(keys)
        result={}
        map(t,keys,values)
        return result

    def __str__(self):
        return 'redis info:{0}\ncache:{1}'.format(self._mconn,json.dumps(self.data,indent=2))

    __repr__ = __str__
#r = RedisCache(master="192.168.48.100:6379")
