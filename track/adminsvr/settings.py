#!/usr/bin/env python
# -*- coding:utf-8 -*-

LOCAL = True 


if LOCAL:
    switch_path = '/Users/huangshaorong/Source/massival/linksvr/tmp/switch_path'

    debug = True

    bind_ip = 'localhost'
    bind_port = 8083

    db_host = 'localhost'
    db_name = 'massival'
    user_db_name = 'powerlink'
    db_user = 'root'
    db_password = ''

    static_folder = 'assets'
    static_root_dir = 'dev/shm'
    static_html_dir = '/assets'

    app_secret = 'massival_secret'

    cookies_expires = 3600*24

    template_dir = 'tmpl'

    # redis
    redis_host = '0.0.0.0'
    redis_port = 6379
    #redis_port = 18888
    redis_mss_db = 'mss_'
    redis_mss_in_short_expire = 600
    redis_mss_in_long_expire = 3600*24
    admin_white_uid_list = [1,]
    mvoffer_white_uid_list = [1]
    global_query_url = "http://0.0.0.0:8089"
else:
    switch_path = '/data/massival_v3_switchpath/switch_path'

    debug = False

    bind_ip = '127.0.0.1'
    bind_port = 3131

    db_host = '68.64.161.62'
    db_name = 'massival'
    user_db_name = 'powerlink'
    db_user = 'admin'
    db_password = '123456'

    static_folder = 'assets'

    app_secret = 'massival_secret'

    cookies_expires = 3600*24

    template_dir = 'tmpl'
    # redis
    redis_host = 'localhost'
    redis_port = 6379
    redis_port = 18888
    redis_mss_db = 'mss_'
    redis_mss_in_short_expire = 180
    redis_mss_in_long_expire = 3600*1
    admin_white_uid_list = []

    static_root_dir = '/media/ephemeral0/assets'
    static_html_dir = '/assets'

massival_common_price = 0.02
version = 1.01
