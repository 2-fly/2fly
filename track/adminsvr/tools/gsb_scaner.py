#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from os import path as osp
import traceback
import sys
import datetime
import urllib
import urllib2
import ujson as json
import requests

import init_env
from adminsvr.db_client import DBClient, User
from commlib.db.redis_helper import RedisHashTable2
from commlib.db.db_tabledef import gsb_report_table, gsb_admin_table
from commlib.utils.sig_helper import hmac_sha1_sig
import adminsvr.settings as settings
import adminsvr.global_vars as global_vars


REPORT_API_URL = "https://sb-ssl.google.com/safebrowsing/api/lookup"
api_key = 'AIzaSyDZcprnQBMcPGmNsMHxlXMkShOX_HAyQwE'
MAX_DOMAINS_PER_CALL = 500
MAX_SCANS_PER_MIN = 1
REPORT_DELAY_MINS = 5

GSB_REPORT_RESULT_FILE = "/tmp/gsb_report_res.txt"
GSB_LOAD_URLS = ["http://0.0.0.0:8080"]
ITEM_PER_REQ = 160


def log_info(msg):
    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    print '%s\t%s'%(ds, msg)


def ts_to_cst(ts):
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def get_cur_domains(delay_minutes=0):
    user_domains = []

    db_client = DBClient(settings.db_user, settings.db_password, settings.db_host, settings.db_name)
    for user in db_client.select_all(User):
        a = [user_domains.append(i.split(";")[0]) for i in user.lander_domains.split(",") if i]
        b = [user_domains.append(i) for i in user.track_domains.split(",") if i]

    domains = user_domains

    group_size = MAX_DOMAINS_PER_CALL*MAX_SCANS_PER_MIN

    groups = []
    cur_group = []
    for _domain in domains:
        cur_group.append(_domain)
        if len(cur_group) >= group_size:
            groups.append(cur_group)
            cur_group = []

    if len(cur_group) > 0:
        groups.append(cur_group)

    if len(groups) == 0:
        return []

    ts = int(time.time()) - delay_minutes*60
    cur_minute = ts / 60

    cur_group = groups[cur_minute % len(groups)]
    return cur_group


def query_gsb(domains):
    if not domains:
        return {}

    req_items = [str(len(domains))]
    for _domain in domains:
        req_items.append('http://%s/'%_domain)

    request_body = '\n'.join(req_items)

    parameters = {
        'client' : 'massival',
        'appver' : '0.9',
        'key' : api_key,
        'pver' : '3.1',
    }
    enc_paras = urllib.urlencode(parameters)
    url = '%s?%s'%(REPORT_API_URL, enc_paras)
    data = request_body
    r = requests.post(url, data=data)
    if r.status_code != 200:
        return {}

    #print r.content
    '''
    ok
    malware
    ok
    '''

    # {'examplebadurl.org': 'ok', 'ianfette.org': 'malware', 'www.google.com': 'ok'}
    results = {}
    states = r.content.split('\n')
    for i in xrange(len(states)):
        state = states[i]
        state = state.strip()
        domain = domains[i]
        results[domain] = state

    return results


def get_all(redis_cli):
    items = load_from_db(redis_cli, gsb_admin_table)
    records = []
    for k, obj in items.iteritems():

        detail = ''
        status = 'good' if obj['state'] == 'ok' else 'bad'
        status += detail
        records.append((k, status, obj['scan_date']))
        #log_info('%s\t%s\t%s'%(k, status, obj['scan_date']))

    records.sort(key=lambda v:v[1])

    for _domain, _status, _date in records:
        print '%s\t%s\t%s'%(_domain, _status, _date)


def save_domains(redis_cli, results):
    # merge to db
    now = int(time.time())
    domains = {}
    for _domain, _state in results.iteritems():
        item = {
            'domain' : _domain,
            'state' : _state,
            'scan_date' : ts_to_cst(now),
        }
        domains[_domain] = item

    save_to_db(domains, redis_cli, gsb_report_table)

    # save to file
    dics = load_from_db(redis_cli, gsb_report_table)

    save_to_file(dics)


def do_report(redis_cli):
    #ds = ['www.google.com', 'ianfette.org', 'examplebadurl.org']
    ds = get_cur_domains()
    results = query_gsb(ds)
    if not results:
        return

    save_domains(redis_cli, results)


def save_to_file(domains):
    with open(GSB_REPORT_RESULT_FILE, "w") as f:
        f.write(json.dumps(domains))


def load_from_file():
    domains = {}
    with open(GSB_REPORT_RESULT_FILE, "r") as f:
        domains = json.loads(f.read())

    return domains


def save_to_db(domains, redis_cli, table_name):
    for _domain, _obj in domains.iteritems():
        redis_cli.add_one(table_name, _domain, json.dumps(_obj))


def load_from_db(redis_cli, table_name):
    items = redis_cli.get_all(table_name)
    ret_dict = {}
    for k, v in items.iteritems():
        ret_dict[k] = json.loads(v)
    return ret_dict


def gen_sig(method, uri, args_dict):
    # ensure args_dict is utf8 encoding
    appkey = global_vars.APP_KEY
    sig = hmac_sha1_sig(method.lower(), uri.lower(), args_dict, appkey+'&')
    return sig

def load_to_admin_db(redis_cli):
    domains = load_from_file()
    #save_to_db(domains, redis_cli, gsb_admin_table)
    remote_sync(domains)

def remote_sync(domains):
    t = int(time.time())
    parameters = {'time': t}
    sign = gen_sig('POST', global_vars.URL_GSB_SYNC, parameters)
    parameters['sig'] = sign
    collection = []
    section = {}
    n = 0
    for k, v in domains.iteritems():
        if n >= ITEM_PER_REQ:
            collection.append(section)
            n = 0
            section = {}
        section[k] = v
        n += 1
    if section:
        collection.append(section)
    for section in collection:
        data = urllib.urlencode({'data':json.dumps(section)})
        for url in GSB_LOAD_URLS:
            url = url + global_vars.URL_GSB_SYNC
            url = '%s?%s' % (url, urllib.urlencode(parameters))
            resp = urllib.urlopen(url, data).read()
            print resp




if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: %s report | print | load'%sys.argv[0]
        exit(-1)

    redis_cli = RedisHashTable2(host=settings.redis_host, port=settings.redis_port)
    cmd = sys.argv[1]
    if cmd == 'report':
        do_report(redis_cli)
    elif cmd == 'print':
        get_all(redis_cli)
    elif cmd == 'load':
        load_to_admin_db(redis_cli)
    else:
        print 'usage: %s report | print | load'%sys.argv[0]


