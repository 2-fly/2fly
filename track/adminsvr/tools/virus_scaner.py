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

import init_env
from adminsvr.db_client import DBClient, User
from commlib.db.redis_helper import RedisHashTable2
from commlib.db.db_tabledef import virusdomain_scan_table, virusdomain_report_table, virusdomains_table
import adminsvr.settings as settings

redis_cli = RedisHashTable2(host=settings.redis_host, port=settings.redis_port)
virus_domains_key = 'content'

SCAN_API_URL = "https://www.virustotal.com/vtapi/v2/url/scan"
RETRIEVE_API_URL = "https://www.virustotal.com/vtapi/v2/url/report"
api_key = '850fb9e7d76c84ff2c80f11fb6b1e4bff6c9a53fa430f31e9f745bcd6b7433b4'
MAX_DOMAINS_PER_CALL = 4
MAX_SCANS_PER_MIN = 1
REPORT_DELAY_MINS = 5

REPORT_RESULT_FILE = "/tmp/virus_report_res.txt"

def log_info(msg):
    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    print '%s\t%s'%(ds, msg)


def scan(domain_urls):
    url = SCAN_API_URL
    parameters = {
        "url": '\n'.join(domain_urls),
        "apikey": api_key,
    }

    data = urllib.urlencode(parameters)
    req = urllib2.Request(url, data)
    try:
        response = urllib2.urlopen(req)
        obj = response.read()
        if not obj:
            return None
        else:
            return json.loads(obj)
    except Exception, ex:
        print ex
        return None



def retrieve(domain_urls):
    url = RETRIEVE_API_URL
    parameters = {
        "resource": '\n'.join(domain_urls),
        "apikey": api_key,
        #"scan" : '1',
    }

    data = urllib.urlencode(parameters)
    req = urllib2.Request(url, data)
    try:
        response = urllib2.urlopen(req)
        obj = response.read()
        if not obj:
            return None
        else:
            return json.loads(obj)
    except Exception, ex:
        print ex
        return None


def report(domain):
    url = 'https://www.virustotal.com/vtapi/v2/domain/report'
    parameters = {'domain': domain, 'apikey': api_key}
    response = urllib.urlopen('%s?%s' % (url, urllib.urlencode(parameters))).read()
    response_dict = json.loads(response)
    print response_dict



def utc_to_cst(date_str):
    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    dt += datetime.timedelta(seconds=8*3600)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def resource_to_domain(resource):
    resource = resource.replace('http://', '')
    resource = resource.replace('/c1', '')
    resource = resource.replace('/', '')
    return resource


def scan_and_save(domains):
    msg_items = []
    for _domain in domains:
        msg_items.append(_domain[0])

    msg = 'scaning %s'%('\t'.join(msg_items))
    log_info(msg)

    domain_urls = []
    for _domain in domains:
        is_lander = _domain[1]
        if is_lander:
            check_str = _domain[0] + '/c1'
        else:
            check_str = _domain[0] + '/'
        domain_urls.append('http://%s'%check_str)
    #domain_urls = ['http://%s/'%_domain for _domain in domains]

    obj = scan(domain_urls)
    if obj is None:
        msg = 'scan failed %s'%str(domain_urls)
        log_info(msg)
        return -1

    if type(obj) == dict:
        obj = [obj]

    for item in obj:
        if item['response_code'] != 1:
            msg = 'scan failed %s'%str(item)
            log_info(msg)
            continue

        msg = 'scaned %s'%str(item)
        log_info(msg)
        # domain
        domain = resource_to_domain(item['resource'])
        # '2015-07-24 05:56:27'
        item['scan_date'] = utc_to_cst(item['scan_date'])
        #print item['permalink', 'resource', 'url', 'scan_date', 'scan_id', 'verbose_msg']

        redis_cli.add_one(virusdomain_scan_table, domain, json.dumps(item))


def retrieve_and_save(domains):
    msg_items = []
    for _domain in domains:
        msg_items.append(_domain[0])

    msg = 'retrieving %s'%('\t'.join(msg_items))
    log_info(msg)

    domain_urls = []
    for _domain in domains:
        is_lander = _domain[1]
        if is_lander:
            check_str = _domain[0] + '/c1'
        else:
            check_str = _domain[0] + '/'
        domain_urls.append('http://%s'%check_str)

    #domain_urls = ['http://%s/'%_domain for _domain in domains]

    obj = retrieve(domain_urls)
    if obj is None:
        msg = 'retrieve failed %s'%str(domain_urls)
        log_info(msg)
        return -1
    if type(obj) == dict:
        obj = [obj]

    for item in obj:
        if item['response_code'] != 1:
            msg = 'retrieve failed %s'%str(item)
            log_info(msg)
            continue

        msg = 'retrieved %s'%str(item)
        log_info(msg)
        # domain
        domain = resource_to_domain(item['resource'])
        # '2015-07-24 05:56:27'
        item['scan_date'] = utc_to_cst(item['scan_date'])
        #print item['permalink', 'resource', 'url', 'scan_date', 'scan_id', 'verbose_msg']

        db_key = virusdomain_report_table
        redis_cli.add_one(db_key, domain, json.dumps(item))
        virus_report_res_dict = redis_cli.get_all(db_key)
        with open(REPORT_RESULT_FILE, "w") as f:
            virus_report_res = []
            for domain, res in virus_report_res_dict.iteritems():
                s = json.dumps({'domain': domain, 'res' : res}) + "\n"
                virus_report_res.append(s)
            f.writelines(virus_report_res)


def get_cur_domains(delay_minutes=0):
    user_domains = []

    db_client = DBClient(settings.db_user, settings.db_password, settings.db_host, settings.db_name)
    for user in db_client.select_all(User):
        a = [user_domains.append((i.split(";")[0], 1)) for i in user.lander_domains.split(",") if i]
        b = [user_domains.append((i.split(";")[0], 0)) for i in user.track_domains.split(",") if i]

    domains = user_domains

    if 0:
        #f = open(osp.join(init_env.cur_path, 'domains.txt'), 'r')
        domains = redis_cli.get_one(virusdomains_table, virus_domains_key)
        domains = json.loads(domains) if domains else []

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


def crontab_task(func, delay_minutes=0):
    domains = get_cur_domains(delay_minutes)
    domain_groups = []
    cur_items = []
    for _domain in domains:
        cur_items.append(_domain)
        if len(cur_items) >= MAX_DOMAINS_PER_CALL:
            domain_groups.append(cur_items)
            cur_items = []
    if cur_items:
        domain_groups.append(cur_items)

    for _domains in domain_groups:
        try:
            func(_domains)
        except Exception, ex:
            log_info(str(traceback.format_exc()))

        time.sleep(5)
        print ''

    print '\n\n\n'


def get_all():
    items = redis_cli.get_all(virusdomain_report_table)
    records = []
    for k, v in items.iteritems():
        obj = json.loads(v)
        if 'positives' not in obj:
            records.append((k, 'not_retrieved', obj['scan_date']))
            #log_info('%s\tnot_retrieved\t%s'%(k, obj['scan_date']))
            continue

        detail = '(%d/%d)'%(obj['positives'], obj['total'])
        status = 'bad' if obj['positives'] > 0 else 'good'
        status += detail
        records.append((k, status, obj['scan_date']))
        #log_info('%s\t%s\t%s'%(k, status, obj['scan_date']))

    records.sort(key=lambda v:v[1])

    for _domain, _status, _date in records:
        print '%s\t%s\t%s'%(_domain, _status, _date)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'usage: %s scan | report |print'%sys.argv[0]
        exit(-1)

    cmd = sys.argv[1]
    if cmd == 'scan':
        crontab_task(scan_and_save)
    elif cmd == 'report':
        crontab_task(retrieve_and_save, REPORT_DELAY_MINS)
    elif cmd == 'print':
        get_all()
    else:
        print 'usage: %s scan | report'%sys.argv[0]


