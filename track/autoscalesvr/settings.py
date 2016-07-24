#!/usr/bin/env python
# -*- coding:utf-8 -*-

LOCAL = False

if LOCAL:
    # linksvr
    debug = True
    bind_ip = '0.0.0.0'
    bind_port = 8082

    # redis
    redis_host = 'db'
    redis_port = 6379
    #redis_port = 18888
    redis_as_db = 'as_'
    redis_as_expire = 3600*24

    autoscale_groupname = 'v3_linksvr_autoscale'


else:
    # linksvr
    debug = True
    bind_ip = '127.0.0.1'
    bind_port = 3012

    redis_host = '127.0.0.1'
    #redis_port = 6379
    redis_port = 18888
    redis_as_db = 'as_'
    redis_as_expire = 3600*24*3

    autoscale_groupname = 'v3_linksvr_autoscale'

