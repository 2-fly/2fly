#!/usr/bin/env python
# -*- coding:utf-8 -*-

import adminsvr.settings as admin_settings
from redis_helper import CacheTable, RedisHashTable2
from adminsvr.db_client import DBClient
from adminsvr.user_db_client import UserDBClient 

class DBClientSet(object):
    def __init__(self):
        self._db_client = None
        self._cache_db = None
        self._redis_db = None
        self._user_db_client = None
        self._init = False
        self._settings = admin_settings
        self._db_cls = DBClient
        self._user_db_cls = UserDBClient

    def init(self, settings, db_cls, user_db_cls):
        self._db_client = None
        self._cache_db = None
        self._redis_db = None
        self._user_db_client = None
        self._init = False
        self._settings = settings
        self._db_cls = db_cls
        self._user_db_cls = user_db_cls

    def set_init(self, init):
        self._init = init

    def get_db_client(self):
        assert self._init
        if self._db_client is None:
            settings = self._settings
            self._db_client = self._db_cls(settings.db_user, settings.db_password,
                            settings.db_host, settings.db_name)
        return self._db_client

    def get_cache_db(self):
        assert self._init
        if self._cache_db is None:
            settings = self._settings
            self._cache_db = CacheTable(settings.redis_mss_db, host=settings.redis_host, port=settings.redis_port)
        return self._cache_db

    def get_redis_db(self):
        assert self._init
        if self._redis_db is None:
            settings = self._settings
            self._redis_db = RedisHashTable2(host=settings.redis_host, port=settings.redis_port)
        return self._redis_db

    def get_user_db_client(self):
        assert self._init
        if self._user_db_client is None:
            settings = self._settings
            self._user_db_client = self._user_db_cls(settings.db_user, settings.db_password,
                    settings.db_host, settings.user_db_name)
        return self._user_db_client
