#!/usr/bin/env python
# -*- coding:utf-8 -*-


import time
import datetime
import urlparse
import copy
import ujson as json
from os import path as osp
from config_parser import extract_variables, build_pattern, detect_log_config, detect_config_path



class StatBaseItem(object):
    def __init__(self):
        self.count = 0
        self.bytes_recv = 0
        self.bytes_sent = 0
        self.urls = {}

    def __repr__(self):
        return str(self.__dict__)


class StatBucket(object):
    def __init__(self):
        self.clear()

    def clear(self):
        self.minute_idx = 0
        self.count = 0
        self.bytes_recv = 0
        self.bytes_sent = 0
        self.details = {}

        codes = [2, 3, 4, 5]
        for code in codes:
            self.details[code] = StatBaseItem()

    def add(self, record):
        status = record.get('status')
        status_type = int(status)/100
        request_path = parse_request_path(record)
        request_length = int(record.get('request_length'))
        bytes_sent = int(record.get('bytes_sent'))

        self.count += 1
        self.bytes_recv += request_length
        self.bytes_sent += bytes_sent

        # detail status_type
        detail = self.details.get(status_type)
        if detail is None:
            return

        detail.count += 1
        detail.bytes_recv += request_length
        detail.bytes_sent += bytes_sent

        # HTTP 5xx
        if status_type == 5:
            counter  = detail.urls.get(request_path)
            if counter:
                counter += 1
            else:
                counter = 1
            detail.urls[request_path] = counter

    def to_dict(self):
        ret_dict = {}
        ret_dict['total'] = [self.count, self.bytes_recv, self.bytes_sent]

        for code, detail in self.details.iteritems():
            key = '%dxx'%code
            ret_dict[key] = [detail.count, detail.bytes_recv, detail.bytes_sent]

        ret_dict['500_urls'] = copy.deepcopy(self.details[5].urls)
        return ret_dict


class LogReader(object):
    def __init__(self, hour_file_path):
        self.stat_buckets = []
        self.num_buckets = 10
        for i in xrange(self.num_buckets):
            self.stat_buckets.append(StatBucket())
        self.hour_file_path = hour_file_path

    def process(self, record):
        time_local = record.get('time_local')
        ts = int(get_ts(time_local))

        minute_idx = ts/60
        bucket_idx = minute_idx % len(self.stat_buckets)
        stat = self.stat_buckets[bucket_idx]
        if minute_idx < stat.minute_idx:
            return

        if minute_idx > stat.minute_idx:
            #print 'clear', minute_idx
            stat.clear()
            stat.minute_idx = minute_idx

        stat.add(record)

    def load_from_file(self, hour_file):
        try:
            f = open(hour_file, 'r')
        except Exception, ex:
            return None

        data = f.read()
        f.close()

        obj = json.loads(data)
        return obj

    def dump_to_file(self, obj, hour_file):
        s = json.dumps(obj)

        f = open(hour_file, 'w')
        f.write(s)
        f.write('\n')
        f.close()

    def merge_minute_dict(self, dict1, dict2):
        for key, value in dict1.iteritems():
            if key != '500_urls':
                value[0] += dict2[key][0]
                value[1] += dict2[key][1]
                value[2] += dict2[key][2]
            else:
                url_dict1 = value
                url_dict2 = dict2[key]
                for k, v in url_dict2.iteritems():
                    if k not in url_dict1:
                        url_dict1[k] = v
                    else:
                        url_dict1[k] += v

    def merge_to_total(self, total_obj, minute_objs):
        for obj in minute_objs:
            minute_idx = obj.minute_idx
            ts = minute_idx*60
            cur_dt = datetime.datetime.fromtimestamp(ts)
            ds = cur_dt.strftime('%Y%m%d%H%M')
            minute_dict = obj.to_dict()
            #old_obj = total_obj.get(ds)
            #if old_obj:
            #    self.merge_minute_dict(minute_dict, old_obj)
            total_obj[ds] = minute_dict
            #print ds, minute_dict

    def flush(self, ts):
        # flush minute stat data ahead of ts
        buckets = []
        minute_idx = ts/60
        for stat in self.stat_buckets:
            if stat.minute_idx == 0 or stat.count == 0:
                continue

            if stat.minute_idx >= minute_idx:
                continue

            buckets.append(stat)

        buckets.sort(key=lambda x:x.minute_idx, reverse=False)

        date_str = get_datestr()
        hour_file = osp.join(self.hour_file_path, 'svrstat_%s.json'%date_str)

        obj = self.load_from_file(hour_file)
        if obj is None:
            obj = {}

        self.merge_to_total(obj, buckets)

        self.dump_to_file(obj, hour_file)


def parse_request_path(record):
    if 'request_uri' in record:
        uri = record['request_uri']
    elif 'request' in record:
        uri = ' '.join(record['request'].split(' ')[1:-1])
    else:
        uri = None
    return urlparse.urlparse(uri).path if uri else None


def get_ts(line):
    line_parts = line.split()
    dt = line_parts[0]
    date = datetime.datetime.strptime(dt, "%d/%b/%Y:%H:%M:%S")
    date = time.mktime(date.timetuple())
    return date


def get_datestr():
    cur_dt = datetime.datetime.now()
    date_str = cur_dt.strftime('%Y%m%d%H')
    return date_str


def get_last_mtime(path):
    last_time = -1
    try:
        last_time = osp.getmtime(path)
    except Exception, ex:
        pass

    return last_time


def follow_file(the_file, stat_file):
    last_time = get_last_mtime(stat_file)
    with open(the_file) as f:
        f.seek(0, 2)  # seek to eof
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)  # sleep briefly before trying again
                cur_stat_time = get_last_mtime(stat_file)
                if cur_stat_time != -1 and cur_stat_time != last_time:
                    last_time = cur_stat_time
                    f.close()
                    print 'reloaded %s'%the_file
                    new_f = open(the_file, 'r')
                    #new_f.seek(0, 2)
                    f = new_f
                continue
            yield line


def build_source(access_log, arguments):
    return follow_file(access_log, arguments['--stat-file'])


def process_log(lines, pattern, arguments, handler):
    #records = parse_log(lines, pattern)
    for line in lines:
        m = pattern.match(line)
        if m is not None:
            #print m.groupdict()
            handler(m.groupdict())


record_dict = {
    'status': 200,
    'body_bytes_sent': '4348',
    'remote_user': '-',
    'request_length': '642',
    'request_time': 0.0,
    'http_referer': 'http://v3.massival.com/admin/reports/campaign',
    'remote_addr': '207.226.143.162',
    'http_x_forwarded_for': '-',
    'request': 'GET /api/summary.json?type=normal&tags=datatable_campaign%2C&cpid=-1&oid=-1&timezone=8&time=10%2F13%2F2015%20-%2010%2F13%2F2015 HTTP/1.1',
    'bytes_sent': 4556,
    'time_local': '14/Oct/2015:16:18:42 +0800',
    'status_type': 2,
    'request_path': '/api/summary.json'
}



def test_reader():
    reader.process(record_dict)
    record_dict['time_local'] = '14/Oct/2015:16:17:42 +0800'
    reader.process(record_dict)
    record_dict['status_type'] = 5
    record_dict['status'] = 500
    record_dict['time_local'] = '14/Oct/2015:16:18:42 +0800'
    reader.process(record_dict)
    reader.process(record_dict)
    record_dict['time_local'] = '14/Oct/2015:16:19:42 +0800'
    reader.process(record_dict)

    cur_log_ts = 1444810780
    reader.flush(cur_log_ts)


last_flush = int(time.time())/60

def log_handler(record_dict):
    global last_flush
    try:
        reader.process(record_dict)
        now = int(time.time())
        cur_min = now/60
        if cur_min > last_flush:
            reader.flush(now)
            last_flush = cur_min
    except Exception, ex:
        print 'log_handler error: %s'%str(ex)


def test_processor(conf_file, stat_file):
    arguments = {
        '--config': conf_file,
        '--stat-file': stat_file,
    }

    access_log, log_format = detect_log_config(arguments)
    # $remote_addr - $remote_user [$time_local] "$request" $status $request_length $bytes_sent $body_bytes_sent "$http_referer" "$http_user_agent" "$http_x_forwarded_for"
    #print log_format
    #print('available variables:\n ', ', '.join(sorted(extract_variables(log_format))))

    pattern = build_pattern(log_format)
    source = build_source(access_log, arguments)
    process_log(source, pattern, arguments, log_handler)


if __name__ == '__main__':
    output_path = ''
    reader = LogReader(output_path)

    #nginx_conf = detect_config_path()
    nginx_conf = 'nginx.conf'
    stat_file = '/tmp/hourrotate.tmp'
    test_processor(nginx_conf, stat_file)



