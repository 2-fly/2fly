#!/usr/bin/env python
# -*- coding:utf-8 -*-

LOCAL = True

if LOCAL:
    debug = True

    bind_ip = 'localhost'
    bind_port = 8084

    db_host = 'localhost'
    db_name = 'powerlink'
    db_user = 'root'
    db_password = ''

    static_folder = 'assets'

    app_secret = 'popsvr_secret'

    cookies_expires = 3600*24

    template_dir = 'tmpl'

    admin_white_uid_list = [1, 2, 3, 4]
    redis_mss_db = 'dsp_'
    redis_mss_in_short_expire = 600
    redis_mss_in_long_expire = 3600*24

    json_dir = '/Users/heyitan/Workspace/tmp/report/'
    json_dir = '/data/dsp_smaato_report'
    # redis
    redis_host = '0.0.0.0'
    redis_port = 18888
    version="0.0.11"
else:
    debug = True

    bind_ip = '0.0.0.0'
    bind_port = 8080

    db_host = '0.0.0.0'
    db_name = 'powerlink'
    db_user = 'root'
    db_password = ''

    static_folder = 'assets'

    app_secret = 'popsvr_secret'

    cookies_expires = 3600*24

    template_dir = 'tmpl'

    json_dir = '/Users/heyitan/Workspace/tmp/report/'
    admin_white_uid_list = [1, 2, 3, 4]
    redis_mss_db = 'mss_'
    redis_mss_in_short_expire = 600
    redis_mss_in_long_expire = 3600*24

    # redis
    redis_host = 'db'
    redis_port = 6379
    #redis_port = 18888
    version="0.0.15"
    img_dir="/Users/heyitan/Workspace/tmp/img/"


