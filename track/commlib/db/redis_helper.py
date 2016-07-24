#!/usr/bin/env python
# -*- coding:utf-8 -*-

import redis


class RedisQueue(object):
    """Simple Queue with Redis Backend"""
    def __init__(self, name, namespace='queue', **redis_kwargs):
        """The default connection parameters are: host='localhost', port=6379, db=0"""
        self.__db= redis.Redis(**redis_kwargs)
        self.key = '%s:%s' %(namespace, name)

    def qsize(self):
        return self.__db.llen(self.key)

    def empty(self):
        return self.qsize() == 0

    def put(self, item):
        self.__db.rpush(self.key, item)

    def get(self, block=True, timeout=None):
        if block:
            item = self.__db.blpop(self.key, timeout=timeout)
        else:
            item = self.__db.lpop(self.key)

        #if item:
        #    item = item[1]
        return item

    def get_nowait(self):
        return self.get(False)

# pre-specified db_name
class RedisHashTable(object):
    def __init__(self, db_name, **redis_kwargs):
        self.db_name = db_name
        self.db = redis.Redis(**redis_kwargs)

    def get_one(self, k):
        return self.db.hget(self.db_name, k)

    def get_all(self):
        return self.db.hgetall(self.db_name)

    def add_one(self, k, v):
        # return 1 if new else 0
        return self.db.hset(self.db_name, k, v)

    def delete_one(self, k):
        return self.db.hdel(self.db_name, k)

    def delete_all(self):
        return self.db.delete(self.db_name)


# dynamic-specified db_name
class RedisHashTable2(object):
    def __init__(self, **redis_kwargs):
        self.db = redis.Redis(**redis_kwargs)

    def get_one(self, db_name, k):
        return self.db.hget(db_name, k)

    def get_all(self, db_name):
        return self.db.hgetall(db_name)

    def add_one(self, db_name, k, v):
        # return 1 if new else 0
        return self.db.hset(db_name, k, v)

    def delete_one(self, db_name, k):
        return self.db.hdel(db_name, k)

    def delete_all(self, db_name):
        return self.db.delete(db_name)


# operate expiring keys
class CacheTable(object):
    def __init__(self, prefix, **redis_kwargs):
        self.prefix = prefix
        self.db = redis.Redis(**redis_kwargs)

    def get(self, k):
        return self.db.get(self.prefix+k)

    def setex(self, k, v, t):
        return self.db.setex(self.prefix+k, v, t)

    def ttl(self, k):
        return self.db.ttl(self.prefix+k)

