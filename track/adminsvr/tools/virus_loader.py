#!/usr/bin/env python
# -*- coding:utf-8 -*-
import ujson
import init_env
import time
import httplib, urllib

from commlib.db.redis_helper import RedisHashTable2
from commlib.db.db_tabledef import virus_domains_key, virusdomain_report_table, virusdomains_admin_table
from commlib.utils.sig_helper import hmac_sha1_sig
import adminsvr.settings as settings
import adminsvr.global_vars as global_vars


VIRUS_REPORT_RESULT_FILE = "/tmp/virus_report_res.txt"
db_key = virusdomains_admin_table
redis_cli = RedisHashTable2(host=settings.redis_host, port=settings.redis_port)
VIRUS_LOAD_URLS = ['http://0.0.0.0:8080']
LINE_PER_REQ = 50

def gen_sig(method, uri, args_dict):
    # ensure args_dict is utf8 encoding
    appkey = global_vars.APP_KEY
    sig = hmac_sha1_sig(method.lower(), uri.lower(), args_dict, appkey+'&')
    return sig

def main_func():
    with open(VIRUS_REPORT_RESULT_FILE, "r") as f:
        remote_sync(f)
    #    for line in f:
    #        obj = ujson.loads(line)
    #        redis_cli.add_one(db_key, obj['domain'], obj['res'])


def remote_sync(f):
    collection = []
    n = 0
    section = []
    for line in f:
        if not line:
            continue
        if n >= LINE_PER_REQ:
            collection.append(section)
            section = []
            n = 0
        section.append(line)
        n += 1
    if section:
        collection.append(section)
    if not collection:
        return
    for section in collection:
        ret = ujson.dumps(section)
        t = int(time.time())
        parameters = {'time': t}
        sign = gen_sig('POST', global_vars.URL_VIRUS_SYNC, parameters)
        parameters['sig'] = sign
        data = urllib.urlencode({"data":ret})

        for url in VIRUS_LOAD_URLS:
            url = url + global_vars.URL_VIRUS_SYNC
            url = '%s?%s' % (url, urllib.urlencode(parameters))
            resp = urllib.urlopen(url, data).read()
            print "success" if resp == "ok" else "fail"

if __name__ == "__main__":
    main_func()
