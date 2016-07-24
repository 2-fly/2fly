#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from os import path as osp
import traceback
import sys
import datetime
import urllib
import urllib2
import json
import random


api_keys = [
    '938458e4745d3fc059783b4b3bc247508703d2a8bd30c79b6c657a647434fa9f',
]

SCAN_API_URL = "https://www.virustotal.com/vtapi/v2/url/scan"
RETRIEVE_API_URL = "https://www.virustotal.com/vtapi/v2/url/report"
MAX_DOMAINS_PER_CALL = 4
MAX_SCANS_PER_MIN = 1
REPORT_DELAY_MINS = 5


DOMAIN_FILE = "/tmp/virus_tool/domains.txt"
REPORT_RESULT_FILE = "/tmp/.result_file.txt"
DOMAIN_ONLY = False


def log_info(msg):
    dt = datetime.datetime.now()
    ds = dt.strftime('%Y-%m-%d %H:%M:%S')

    print '%s\t%s'%(ds, msg)


def load_domains(file_name):
    f = open(file_name, 'r')
    domains = []
    for line in f:
        s = line.strip()
        if s:
            domains.append(s)
    f.close()
    return domains


class ResultHandler(object):
    def __init__(self):
        self.result_file = REPORT_RESULT_FILE

    def get_all(self):
        try:
            with open(self.result_file, 'r') as f:
                s = f.read()
                objs = json.loads(s)
                return objs
        except IOError:
            return {}

    def save_all(self, objs):
        with open(self.result_file, 'w') as f:
            s = json.dumps(objs)
            f.write(s)

    def add(self, domain, item, is_scan=True):
        if is_scan:
            # ignore scan operation
            pass
        else:
            old_objs = self.get_all()
            old_objs[domain] = item
            self.save_all(old_objs)


result_handler = ResultHandler()


def scan(domain_urls, api_key):
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



def retrieve(domain_urls, api_key):
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
    parameters = {'domain': domain, 'apikey': random.choice(api_keys)}
    response = urllib.urlopen('%s?%s' % (url, urllib.urlencode(parameters))).read()
    response_dict = json.loads(response)
    print response_dict



def utc_to_cst(date_str):
    dt = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    dt += datetime.timedelta(seconds=8*3600)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def resource_to_domain(resource):
    # TODO
    if DOMAIN_ONLY:
        resource = resource.replace('http://', '')
        resource = resource.replace('/c1', '')
        resource = resource.replace('/', '')
        return resource
    else:
        return resource


def scan_and_save(domains, global_group_idx):
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
        # TODO
        if DOMAIN_ONLY:
            domain_urls.append('http://%s'%check_str)
        else:
            domain_urls.append(_domain[0])
    #domain_urls = ['http://%s/'%_domain for _domain in domains]

    api_key = api_keys[global_group_idx%len(api_keys)]
    obj = scan(domain_urls, api_key)
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

        result_handler.add(domain, item)


def retrieve_and_save(domains, global_group_idx):
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
        # TODO
        if DOMAIN_ONLY:
            domain_urls.append('http://%s'%check_str)
        else:
            domain_urls.append(_domain[0])

    #domain_urls = ['http://%s/'%_domain for _domain in domains]

    api_key = api_keys[global_group_idx%len(api_keys)]
    obj = retrieve(domain_urls, api_key)
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

        result_handler.add(domain, item, False)
        continue

        virus_report_res_dict = result_handler.get_all()
        with open(REPORT_RESULT_FILE, "w") as f:
            virus_report_res = []
            for domain, res in virus_report_res_dict.iteritems():
                s = json.dumps({'domain': domain, 'res' : res}) + "\n"
                virus_report_res.append(s)
            f.writelines(virus_report_res)


def get_cur_domains(delay_minutes=0):
    user_domains = []

    dm = load_domains(DOMAIN_FILE)
    for d in dm:
        user_domains.append((d, 0))

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

    cur_minute = int(time.time()) / 60
    real_minute = (int(time.time()) - delay_minutes*60) / 60

    global_group_idx = real_minute % len(groups)
    cur_group = groups[global_group_idx]
    return cur_group, global_group_idx


def crontab_task(func, delay_minutes=0):
    domains, global_group_idx = get_cur_domains(delay_minutes)
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
            func(_domains, global_group_idx)
        except Exception, ex:
            log_info(str(traceback.format_exc()))

        time.sleep(5)
        print ''

    print '\n\n\n'


def get_all():
    items = result_handler.get_all()
    records = []
    for k, v in items.iteritems():
        obj = v
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


