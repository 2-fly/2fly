#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import settings
import datetime
import ujson as json
import tarfile
from os import path as osp
from global_vars import global_db_set as DBSet
from stat_result import StatResult
from db_client import *
from config.offer_link_config import OfferLink
from config.affiliate_config import AFFILIATE_LIST
from config.permission_config import *
from config.table_config import *
from config.auth_config import RELATIVE_USER_CONFIG, RELATIVE_EVENT_USER_CONFIG, MASSIVAL_INNER_USER_PERMISSION
from commlib.utils.my_crypto import MyCrypto
from commlib.utils.utils import format_int_comma, format_float_comma
from utils import check_permission, decode_from_utf8

import global_vars

reload(sys)
sys.setdefaultencoding('utf-8')

ONE_DAY_SECONDS = 3600 * 24
ONE_HOUR_SECOND = 3600
IGNORE_RULE_ID = -1
TIMEZONE = -time.timezone / 3600
KEY_MRID = '2flystatic'

def str_to_date(s):
    return datetime.datetime.strptime(s, '%Y%m%d%H')

def date_to_ts(dt):
    return int(time.mktime(dt.timetuple()))

def ts_to_date(ts):
    return datetime.datetime.fromtimestamp(ts)

def ts_to_str_day(ts):
    x = time.localtime(ts)
    return time.strftime("%Y%m%d", x)

def str_day_to_ts(s):
    dt = datetime.datetime.strptime(s, "%Y%m%d")
    return date_to_ts(dt)

def str_hour_to_ts(s):
    dt = datetime.datetime.strptime(s, "%Y%m%d%H")
    return date_to_ts(dt)

def str_second_to_ts(s):
    dt = datetime.datetime.strptime(s, "%Y%m%d%H%M%S")
    return date_to_ts(dt)

def ts_to_ts_day(ts):
    ts_str = ts_to_str_day(ts)
    return str_day_to_ts(ts_str)

def ts_to_str_hour(ts):
    x = time.localtime(ts)
    return time.strftime("%Y%m%d%H", x)

def ts_to_str_min(ts):
    x = time.localtime(ts)
    return time.strftime("%Y-%m-%d %H:%M", x)

def ts_to_str_second(ts):
    x = time.localtime(ts)
    return time.strftime("%Y-%m-%d %H:%M:%S", x)

def encrypt(data):
    ec = MyCrypto(KEY_MRID)
    en = ec.encode(data)
    return en

def decrypt(data):
    ec = MyCrypto(KEY_MRID)
    raw = ec.decode(data)
    return raw

ALL_TAGS = [
    'all', 'campaign', 'path',
    'landing_page', 'offer', 'network', 'browser',
    'traffic_source', 'os', 'country', 'domain',
    'ref', 'lander_ref', 'ts_ref', 'country_isp',
    'websiteid', 'tok1', 'tok2', 'tok3'
]

FLOW_PRICE = {
    'cal': 0.09,
    'ore': 0.09,
    'vir': 0.09,
    'ire': 0.09,
    'fr' : 0.09,
    'sng': 0.14,
    'jp' : 0.14,
    'sao': 0.25,
    'syd': 0.14,
    'ip' : 0.09,
}

FLOW_AREAS = sorted(FLOW_PRICE.keys(), cmp=lambda x,y :1 if x == "ip" else -1 )

FLOW_HELP_TIPS = "流量费用将按照cal : 0.09$/GB, ore : 0.09$/GB, vir : 0.09$/GB, ire : 0.09$/GB, fr : 0.09$/GB, sng : 0.14$/GB, jp : 0.14$/GB, sao : 0.25$/GB, syd : 0.14$/GB, ip : 0.09$/GB的单价进行收费。"

STATIC_DATA_BY_DAY = 0
STATIC_DATA_BY_HOUR = 1

RULES_NO_LENGTH_LIMIT = -1

class BaseResult(object):
    def __init__(self):
        self._items = ['Visits', 'Clicks', 'Convs', 'Unique_Visits',
        'Profit', 'Revenue', 'Cost',
        'CPM', 'CTR', 'CR', 'CV', 'ROI',
        'EPM', 'EPC', 'AP',
        'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain',
        'Orientation', 'Wid_typo', 'Wid_digit', 'Cookie', 'Fake', "Cloak_ts2",
        #'BlackIps',
        #'rerrors', 'cerrors', 'pberrors',
        'Errors'
        ]

        #self._dashboard_head = ['Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'ROI']
        self._dashboard_head = []
        self._chart_head = []
        self._sort_default = []
        self._result_list = []
        self._result_map = {}

        self._tag = 'all'
        self._uid = 0
        self._raw_uid = 0
        self._user_name = ""

        self._start_day = 0
        self._end_day = 0
        self._start_hour = 0
        self._end_hour = 23
        self.__init_day()

        #self._cache_db = None
        #self._report_db = None
        # for static_result
        self._cache_db = DBSet.get_cache_db()
        # for daily report
        self._report_db = DBSet.get_redis_db()
        self._cur_ts = int(time.time())
        self._rules = {}
        self._timezone = 8
        self._is_full_day = True

        self._cp_names = None
        self._is_show_date = False
        self._nummeric_comma = []
        self._ignore_items = []
        self._filter_items = {}
        self._op = {
            "paging" : (True, [[20,50,100, -1], [20,50,100,'All']]),
            }
        #find json obj key from result.
        #class : find name from db
        #is_rules: is rules
        self._json_keys = [] # {key:k, class:ins, is_rule:False}
        self._format_columns = []# {col:c, color:red, reg:""}
        self._data_type = STATIC_DATA_BY_DAY
        self._template_format = {}
        self.__init_template_format()

        self._prefix_filename = ""
        self._tar_prefix_filename = ""
        self._hour_data = {}
        self._custom_head = ['visits', 'clicks', 'conversions', 'revenue', 'warns', 'android', 'uniq_visits']
        self._files_path = settings.json_dir
        self._url_args = {}

    def check_is_inner_user(self, uid):
        user = DBSet.get_db_client().select_one(User,id=uid)
        return user.permission in MASSIVAL_INNER_USER_PERMISSION

    def set_url_args(self, args):
        args = args or {}
        self._url_args = args

    def get_url_args(self):
        return self._url_args

    def get_kendo_charts(self):
        return {'charts':[]}

    def get_offset_timezone(self):
        return (TIMEZONE - self._timezone) * 3600

    def crypto(self, data):
        ec = MyCrypto(KEY_MRID)
        return ec.encode(data)

    def prase(self, data):
        ec = MyCrypto(KEY_MRID)
        raw = ec.decode(data)
        return raw

    def is_relative_user(self):
        return self.get_raw_uid() in RELATIVE_USER_CONFIG

    def is_crypt_user(self):
        user = DBSet.get_db_client().select_one(User, id=self._my_uid)
        return check_permission(PERMISSION_REPORT, user.permission, PERMISSION_REPORT_ENCRYPT)

    def get_user_permission(self, uid):
        user = DBSet.get_db_client().select_one(User, id=uid)
        return user.permission

    def _add_template_format(self, k, v):
        self._template_format[k] = v

    def __init_template_format(self):
        self._add_template_format("Visits", "n0")
        self._add_template_format("Clicks", "n0")
        self._add_template_format("Convs", "n0")
        self._add_template_format("Unique_Visits", "n0")
        self._add_template_format("Profit", "c2")
        self._add_template_format("Revenue", "c2")
        self._add_template_format("Cost", "c2")
        self._add_template_format("CPM", "c2")
        self._add_template_format("CTR", "p2")
        self._add_template_format("CR", "p2")
        self._add_template_format("CV", "p2")
        self._add_template_format("ROI", "p2")
        self._add_template_format("EPM", "c2")
        self._add_template_format("EPC", "c2")
        self._add_template_format("AP", "c2")
        self._add_template_format("Warns", "n0")
        self._add_template_format("Track_domain", "n0")
        self._add_template_format("Lander_domain", "n0")
        self._add_template_format("Cloak_ts", "n0")
        self._add_template_format("Cloak", "n0")
        self._add_template_format("Orientation", "n0")
        self._add_template_format("Wid_typo", "n0")
        self._add_template_format("Wid_digit", "n0")
        self._add_template_format("BlackIps", "n0")
        self._add_template_format("Errors", "n0")
        self._add_template_format("Price","c2")
        self._add_template_format("Total","n0")
        self._add_template_format("TotalCost","c2")
        self._add_template_format("FlowCost","c2")
        self._add_template_format("TrackCost","c2")
        self._add_template_format("Flow", "\#\#,\#.00 GB")
        self._add_template_format("Tracks","n0")
        self._add_template_format("Cookie", "n0")
        self._add_template_format("cap", "n0")
        self._add_template_format("Fake", "n0")
        self._add_template_format("Cloak_ts2", "n0")

    def get_template_format(self):
        return self._template_format

    def set_timezone(self, timezone):
        self._timezone = timezone

    def get_result_map(self):
        return self._result_map

    def get_result_list(self):
        return self._result_list

    def __init_day(self):
        today = datetime.date.today()
        self._end_day = int(time.mktime(today.timetuple()))
        self._start_day = self._end_day

    def __init_numeric_comma(self):
        items = ['Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost',
                 'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain', 'Orientation', 'Wid_typo', 'Wid_digit']
        result = self.__find_columns_by_names(items)
        self._nummeric_comma = result.values()

    def add_filter_items(self, name, op):
        result = self.__find_columns_by_names([name])
        col = result[name]
        self._filter_items[col] = op

    def get_filter_items(self):
        return self._filter_items

    def set_data_type(self, data_type):
        self._data_type = data_type

    def get_data_type(self):
        return self._data_type

    def set_cpnames(self, names):
        self._cp_names = names

    def get_cpnames(self):
        return self._cp_names

    def finish_init(self):
        formats = {
            "Profit" : {"reg":"$"},
            "ROI" : {"reg":"%"}
            }
        self.add_column_format(formats)
        self.__init_numeric_comma()

    def get_all_uids(self, filter_uid_list=None):
        res = DBSet.get_db_client().iter_all(User)
        uids = []
        for obj in res:
            if filter_uid_list and obj.id in filter_uid_list:
                uids.append((obj.id, obj.name))
        return uids

    def __find_columns_by_names(self, names):
        res = {}
        for k in names:
            for i in xrange(len(self._items)):
                if k == self._items[i]:
                    res[k] = i
        return res

    def add_column_format(self, formats):
        cols = self.__find_columns_by_names(formats.keys())
        for k, v in cols.items():
            tmp = {
                "col" : v,
                "reg" : formats[k]["reg"]
            }
            self._format_columns.append(tmp)

    def get_column_format(self):
        return self._format_columns

    def get_op(self):
        return self._op

    def set_paging(self, page):
        self._op["paging"] = page

    def set_date(self, is_show=True):
        self._is_show_date = is_show

    def add_json_keys(self, keys):
        for k in keys:
            self._json_keys.append(k)

    def insert_items(self, items):
        for i in range(len(items)-1, -1, -1):
            self._items.insert(0, items[i])

    def add_items(self, items, ignore=True):
        item_len = len(self._items)
        for v in items:
            self._items.append(v)
        if ignore:
            for i in xrange(len(items)):
                self._ignore_items.append(item_len+i)

    def get_sort_format(self):
        result = []
        ignore = {
            'targets' : self._ignore_items,
            'visible' : False,
        }
        comma = {
            'targets' : self._nummeric_comma,
            'type' : "numeric-comma",
        }
        result.append(ignore)
        result.append(comma)
        return result

    def set_items(self, items):
        self._items = items

    def get_items(self):
        return self._items

    def set_dashboard_chart_items(self, items):
        self._chart_head = items

    def get_dashboard_chart_items(self):
        return self._chart_head

    def set_prefix_filename(self, prefix):
        self._prefix_filename = prefix

    def get_prefix_filename(self):
        return self._prefix_filename

    def set_tar_prefix_name(self, tar_prefix):
        self._tar_prefix_filename = tar_prefix

    def get_tar_prefix_name(self):
        return self._tar_prefix_filename

    def get_file_full_name(self, file_name):
        #return  "%s%s.json" % (self.get_prefix_filename(), file_name)
        return  "%s%s.tar.gz" % (self.get_prefix_filename(), file_name)

    def get_day_file_path(self):
        return osp.join(self.get_files_path(), str(self.get_uid()))

    def get_hour_file_path(self):
        path = osp.join(self.get_files_path(), str(self.get_uid()))
        return osp.join(path, "hour")

    def get_file_modify_time(self, path):
        last_time = -1
        try:
            last_time = osp.getmtime(path)
        except Exception, ex:
            pass
        return last_time

    def check_file_is_modify(self, path, file_name):
        last_time = self.get_file_modify_time(path)
        cache_time = self.get_cache(self.get_mss_cachetime_key(file_name))
        if cache_time is None:
            cache_time = -1
        return cache_time != last_time

    def get_mss_db_key(self, ts, tag=None):
        tag = tag or self.get_tag()
        is_full_day = self.get_full_day()
        data_type = 0 if is_full_day else 1
        return "%s_%s_%s_%s_%s_%s" % (self.get_prefix_filename(), self.get_tar_prefix_name(), self.get_uid(), data_type, tag, ts)

    def get_mss_cachetime_key(self, file_name):
        is_full_day = self.get_full_day()
        data_type = 0 if is_full_day else 1
        return "%s_%s_%s_%s_%s" % (self.get_prefix_filename(), self.get_tar_prefix_name(), self.get_uid(), data_type, file_name)

    def _set_data_cache(self, obj, file_name, ts):
        #set modify time cache
        file_path = self._do_get_file_path(file_name)
        last_time = self.get_file_modify_time(file_path)
        if last_time != -1:
            self.set_cache(self.get_mss_cachetime_key(file_name), last_time, ts)
        for tag in ALL_TAGS:
            s = obj.get(tag, None)
            if s is None:
                continue
            s_key = self.get_mss_db_key(ts, tag)
            self.set_cache(s_key, json.dumps(s), ts)

    def get_static_data(self, file_name, key, ts):
        if 1:
            key_ts = 0
            if self.get_full_day():
                key_ts = str_day_to_ts(key)
            else:
                key_ts = str_hour_to_ts(key)
            #if self.get_data_type() == STATIC_DATA_BY_DAY:
            #    if self.get_full_day():
            #        key_ts = str_day_to_ts(key)
            #    else:
            #        key_ts = str_hour_to_ts(key)
            #elif self.get_data_type() == STATIC_DATA_BY_HOUR:
            #    key_ts = str_hour_to_ts(key)
            return self.get_file_static_data(file_name, key_ts, ts)
            #return self.get_file_static_data(file_name, key, ts)
        else:
            return self.get_db_static_data(file_name, ts)

    def _do_get_file_path(self, file_name):
        file_name = self.get_file_full_name(file_name)
        path = ""
        data_type = self.get_data_type()
        if data_type == STATIC_DATA_BY_DAY:
            if self.get_full_day():
                path = osp.join(self.get_day_file_path(), file_name)
            else:
                path = osp.join(self.get_hour_file_path(), file_name)
        elif data_type == STATIC_DATA_BY_HOUR:
            path = osp.join(self.get_hour_file_path(), file_name)
        return path

    def _get_file_full_name(self, file_name):
        #return "%s.json" % file_name
        return "%s%s%s.json" % (self.get_prefix_filename(), self.get_tar_prefix_name(), file_name)

    def get_file_static_data(self, file_name, k, ts):
        key = self.get_mss_db_key(k)
        data = self.get_cache(key)
        file_path = self._do_get_file_path(file_name)
        file_full_name = self._get_file_full_name(file_name)
        data = None
        if data is None or self.check_file_is_modify(file_path, file_name):
            obj = self.get_static_data_from_file_gz(file_path, file_full_name)
            if obj:
                data = obj.get(self.get_tag(), None)
                self._set_data_cache(obj, file_name, ts)
        return data

    def get_db_static_data(self, file_name, ts):
        data = None
        obj = self.get_static_data_from_report_db(ts)
        if obj:
            data = obj.get(self.get_tag(), None)
        return data

    def get_static_data_from_report_db(self, ts):
        cur_dt = ts_to_date(ts)
        data_str = ""
        data_type = self.get_data_type()
        if data_type == STATIC_DATA_BY_DAY:
            date_str = cur_dt.strftime('%Y%m%d')
        elif data_type == STATIC_DATA_BY_HOUR:
            date_str = cur_dt.strftime('%Y%m%d%H')

        db_key = 'daystat_%d'%self._uid
        all_text = self._report_db.get_one(db_key, date_str)
        if all_text:
            try:
                obj = json.loads(all_text)
                return obj
            except Exception, ex:
                print ex
                return None
        else:
            return None

    def get_static_data_from_file(self, file_path):
        data = None
        try:
            with open(file_path, 'r') as f:
                all_text = decode_from_utf8(f.read())
                data = json.loads(all_text)
        except Exception, ex:
            print ex
        return data

    def get_static_data_from_file_gz(self, file_path, file_name):
        data = None
        try:
            tarObj = tarfile.open(file_path, "r:*")
            obj = tarObj.getmember(file_name)
            f = tarObj.extractfile(obj)
            lines = f.readlines()
            s = "".join(lines)
            s = decode_from_utf8(s)
            data = json.loads(s)
            return data
        except Exception, ex:
            print ex
        return data

    def find_name_map(self, keys):
        names_map = {}
        for _info in keys:
            key = _info.get("key", None)
            ins = _info.get("class", None)
            admin_uid = _info.get("admin_uid", None)
            if not key or not ins:
                continue
            uid = admin_uid or self.get_uid()
            if key == "cpid":
                if uid == -1:
                    tmp = self.get_cpnames() or self.get_db_record_names(ins)
                else:
                    tmp = self.get_cpnames() or self.get_db_record_names(ins, uid=uid)
            else:
                if uid == -1:
                    tmp = self.get_db_record_names(ins)
                else:
                    tmp = self.get_db_record_names(ins, uid=uid)
            names_map[key] = tmp
        return names_map

    def is_length_limit(self, result_list):
        limit = self._rules.get("limit", RULES_NO_LENGTH_LIMIT)
        if limit == RULES_NO_LENGTH_LIMIT:
            return False
        return len(result_list) >= limit

    def set_full_day(self, is_full):
        self._is_full_day = is_full

    def get_full_day(self):
        return self._is_full_day

    def check_is_full_day(self, day, range_days):
        #return self._timezone == TIMEZONE or (0 < day < range_days)
        return self._timezone == TIMEZONE

    def is_origin_timezone(self):
        return self._timezone == TIMEZONE

    def load_custom_result(self):
        self.load_result()

    def load_base_offset_result(self):
        self.set_full_day(False)
        diff_ts = self.get_offset_timezone()
        start_ts = self.get_start_day() + self._start_hour * ONE_HOUR_SECOND
        end_ts = self.get_end_day() + self._end_hour * ONE_HOUR_SECOND
        offset_ts = start_ts + diff_ts
        hours = (end_ts - start_ts) / 3600
        for h in xrange(hours+1):
            c = start_ts + h * ONE_HOUR_SECOND
            s = offset_ts + h * ONE_HOUR_SECOND
            day_ts = ts_to_ts_day(c)
            hour_dt = datetime.datetime.fromtimestamp(s)
            datetime_str = hour_dt.strftime('%Y%m%d%H')
            ts = date_to_ts(hour_dt)
            self.static_result(datetime_str, ts, day_ts)

    def is_full_day(self):
        return self._start_hour == 0 and self._end_hour == 23

    def is_offset_date(self):
        return not self.is_origin_timezone() or not self.is_full_day()

    def load_result(self):
        if not self.is_offset_date():
            self.load_normal_result()
        else:
            self.load_offset_result()

    def load_result2(self):
        if self.is_origin_timezone():
            self.load_normal_result()
        else:
            self.load_offset_result()

    def load_normal_result(self):
        range_days = self.get_range_days()
        start_day = self.get_start_day()
        self.load_full_day(start_day, range_days)

    def load_full_day(self, start_day, range_days):
        self.set_full_day(True)
        for i in xrange(range_days):
            cur_dt = datetime.datetime.fromtimestamp(start_day+ i*ONE_DAY_SECONDS)
            datetime_str = cur_dt.strftime('%Y%m%d')
            ts = date_to_ts(cur_dt)
            self.static_result(datetime_str, ts, ts)

    def load_part_day(self, offset_ts, key_ts, from_hour=0, to_hour=23, save_hour_data=False):
        self.set_full_day(False)
        n = 0
        for j in xrange(0, to_hour-from_hour+1, 1):
            hour_dt = datetime.datetime.fromtimestamp(offset_ts + j*ONE_HOUR_SECOND)
            datetime_str = hour_dt.strftime('%Y%m%d%H')
            h_ts = date_to_ts(hour_dt)
            if save_hour_data:
                ret = self.prev_hour_seg_static_result(datetime_str, h_ts, key_ts)
                if ret is not None:
                    self._hour_data[int(datetime_str)] = ret
                    n += 1
            else:
                self.static_result(datetime_str, h_ts, key_ts)
        return n

    def _cal_day_offset_time(self, start_day, day):
        diff_time = self.get_offset_timezone()
        diff_dt = datetime.datetime.fromtimestamp(start_day+diff_time + day*ONE_DAY_SECONDS)
        diff_ts = date_to_ts(diff_dt)
        return diff_ts

    def _get_first_offset_hour(self):
        start_hour = (TIMEZONE - self._timezone) % 24
        end_hour = 23
        return start_hour, end_hour

    def _get_last_offset_hour(self):
        start_hour = 0
        end_hour = (TIMEZONE - self._timezone) % 24
        return start_hour, end_hour

    def _do_load_first_offset_day(self,start_day, range_days):
        start_hour, end_hour = self._get_first_offset_hour()
        cur_dt = datetime.datetime.fromtimestamp(start_day)
        ts = date_to_ts(cur_dt)
        offset_ts = start_day + self.get_offset_timezone()
        self.load_part_day(offset_ts, ts, start_hour, end_hour)

    def _do_load_last_offset_day(self, start_day, range_days, save_hour_data=False):
        start_hour, end_hour = self._get_last_offset_hour()
        if self._timezone > TIMEZONE:
            range_days = range_days - 1
        cur_dt = datetime.datetime.fromtimestamp(start_day + range_days*ONE_DAY_SECONDS)
        ts = date_to_ts(cur_dt)
        return self.load_part_day(ts, ts, start_hour, end_hour, save_hour_data)

    def _cal_day_range_ts(self):
        offset_start_hour = (TIMEZONE - self._timezone + self._start_hour)
        offset_end_hour = (TIMEZONE - self._timezone + self._end_hour)
        start_ts = self.get_start_day() + offset_start_hour * ONE_HOUR_SECOND
        end_ts = self.get_end_day() + offset_end_hour * ONE_HOUR_SECOND
        return start_ts, end_ts

    def _cal_range_days(self, start_ts, end_ts):
        s_ts = ts_to_ts_day(start_ts)
        e_ts = ts_to_ts_day(end_ts)
        diff_day = (e_ts - s_ts) / ONE_DAY_SECONDS
        return diff_day

    def get_start_hour(self):
        start_hour = (TIMEZONE - self._timezone + self._start_hour) % 24
        return start_hour

    def get_end_hour(self):
        end_hour = (TIMEZONE - self._timezone + self._end_hour) % 24
        return end_hour

    def load_offset_result(self):
        start_hour = self.get_start_hour()
        end_hour = self.get_end_hour()
        start_ts, end_ts = self._cal_day_range_ts()
        diff_day = self._cal_range_days(start_ts, end_ts)
        if diff_day == 0:
            self.load_part_day(start_ts, self._start_day, start_hour, end_hour)
        elif diff_day == 1:
            if start_hour == 0:
                self.load_full_day(start_ts, 1)
            else:
                self.load_part_day(start_ts, self._start_day, start_hour, 23)
            e_ts = end_ts - end_hour * ONE_HOUR_SECOND
            if end_hour == 23:
                self.load_full_day(e_ts, 1)
            else:
                self.load_part_day(e_ts, self._end_day, 0, end_hour)
        else:
            s_ts = start_ts - start_hour * ONE_HOUR_SECOND
            e_ts = end_ts - end_hour * ONE_HOUR_SECOND
            if start_hour == 0:
                self.load_full_day(s_ts, 1)
            else:
                self.load_part_day(start_ts, self._start_day, start_hour, 23)
            self.load_full_day(s_ts+ONE_DAY_SECONDS, diff_day-1)
            if end_hour == 23:
                self.load_full_day(e_ts, 1)
            else:
                self.load_part_day(e_ts, self._end_day, 0, end_hour)

    def load_offset_result2(self):
        range_days = self.get_range_days()
        start_day = self.get_start_day()

        self._do_load_first_offset_day(start_day, range_days)
        self._do_load_last_offset_day(start_day, range_days)
        if range_days > 1:
            if self._timezone < TIMEZONE:
                start_day = start_day + ONE_DAY_SECONDS
            self.load_full_day(start_day, range_days-1)

    def check_is_valid(self, obj, keys):
        key_list = []
        for _info in keys:
            key = _info.get("key", None)
            is_rule = _info.get("is_rule", False)
            if not key:
                continue

            keyObj = obj.get(key, None)
            if keyObj is None:
                return dict(ok=False)
            if is_rule and not self.is_valid_rules({key : keyObj}):
                return dict(ok=False)
            key_list.append(keyObj)
        return dict(ok=True, key_list=key_list)

    def static_result(self, datetime_str, k_ts, ts):
        json_keys = self._json_keys
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for obj in objs:
                res = self.check_is_valid(obj, json_keys)
                if not res["ok"]:
                    continue
                if self._is_show_date:
                    keys = ts
                else:
                    keys = "-".join([str(s) for s in res["key_list"]])
                if keys not in self._result_map:
                    tmp = StatResult()
                    self._result_map[keys] = (res["key_list"], tmp, ts)
                self._result_map[keys][1].add_raw(obj)

    def get_raw_custom_data(self, filter_col=None):
        result = {}
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            cpid = key_list[0]
            if cpid not in result:
                result[cpid] = {}
            items = []
            for k in self._custom_head:
                v = getattr(_result, k)
                items.append(v)
            result[cpid][key_list[1]] = items
        return result

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        result_list = []
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()
            for i in range(len(key_list)-1, -1,-1):
                k = key_list[i]
                jk_k = self._json_keys[i].get("key", None)
                if jk_k and jk_k in names_map:
                    name = names_map[jk_k].get(k, "%s"%k)
                    items.insert(0, name)
                else:
                    items.insert(0, k)
            if self._is_show_date:
                dt = ts_to_date(ts)
                datetime_str = dt.strftime('%Y%m%d')
                items = _result.to_raw_items()
                items.insert(0, datetime_str[4:])

            for i in xrange(len(key_list)):
                if self._json_keys[i].get("add_ignore", None):
                    continue
                k = key_list[i]
                items.append(k)
            if filter_col:
                filter_items = []
                for col in filter_col:
                    filter_items.append(items[col])
                items = filter_items
            result_list.append(items)
        return result_list

    def __get_default_sort_name2op(self):
        result = []
        for _info in self._sort_default:
            col, op = _info[0], _info[1]
            name = self._items[col]
            result.append((name, op))
        return result

    def get_default_sort(self):
        return self.__get_default_sort_name2op()

    def set_dashboard_head(self, items):
        self._dashboard_head = items

    def add_dashboard_head(self, items):
        for i in xrange(len(items)):
            self._dashboard_head.append(items[i])

    def get_dashboard_head(self):
        return self._dashboard_head

    def get_dashboard_data(self, sort_type=1):
        def __desc_cmp(a,b):
            if a[1] > b[1]:
                return -1
            else:
                return 1
        def __asc_cmp(a,b):
            if a[1] > b[1]:
                return 1
            else:
                return -1

        cols = self.__find_columns_by_names(self.get_dashboard_head()).values()
        cols.sort()
        raw_data = self.get_raw_data(cols)
        if sort_type == 1:
            raw_data.sort(__desc_cmp)
        elif sort_type == -1:
            raw_data.sort(__asc_cmp)
        data = []
        for d in raw_data:
            tmp = {}
            for i in xrange(len(cols)):
                tmp[self._items[cols[i]]] = d[i]
            data.append(tmp)
            if self.is_length_limit(data):
                break
        return data

    def get_dashboard_column_format(self):
        items = self._dashboard_head
        result = {}
        for item in items:
            result[item] = self._template_format.get(item, "")
        return result

    def get_help_tips(self):
        return ""

    def get_kendo_data(self):
        raw_data = self.get_raw_data()
        result = {}
        result["head"] = self._items
        result["data"] = []
        result["hidden"] = self._ignore_items
        result["filter"] = self._filter_items
        result["format"] = self.get_template_format()
        result["default_sort"] =  self.__get_default_sort_name2op()
        result["bottom_static"] = self.get_bottom_static()
        result["tips"] = self.get_help_tips()
        for d in raw_data:
            tmp = {}
            for i in xrange(len(d)):
                tmp[self._items[i]] = d[i]
            result["data"].append(tmp)
            if self.is_length_limit(result["data"]):
                break
        return result

    def set_uid(self, uid):
        self.set_raw_uid(uid)
        self._uid = RELATIVE_USER_CONFIG.get(uid, uid)

    def set_my_uid(self, uid):
        self._my_uid = uid

    def get_uid(self):
        return self._uid

    def get_raw_uid(self):
        return self._raw_uid

    def set_raw_uid(self, uid):
        self._raw_uid = uid

    def set_user_name(self, name):
        self._user_name = name

    def get_user_name(self):
        return self._user_name

    def get_result(self):
        pass

    def set_tag(self, tag):
        self._tag = tag

    def get_tag(self):
        return self._tag

    def set_load_range(self, start_day, end_day):
        self._start_day = start_day
        self._end_day = end_day

    def set_start_day(self, start_ts):
        self._start_day = start_ts

    def set_end_day(self, end_ts):
        self._end_day = end_ts

    def set_start_hour(self, start_hour):
        self._start_hour = start_hour

    def set_end_hour(self, end_hour):
        self._end_hour = end_hour

    def get_start_day(self):
        return self._start_day

    def get_end_day(self):
        return self._end_day

    def get_range_days(self):
        return (self._end_day - self._start_day) / ONE_DAY_SECONDS + 1

    def parse_time(self, time_str):
        if ' ' in time_str:
            parts = time_str.split(' - ')
            start_dt = datetime.datetime.strptime(parts[0], "%m/%d/%Y")
            end_dt = datetime.datetime.strptime(parts[1], "%m/%d/%Y")
            if start_dt > end_dt:
                raise Exception('invalid start end time: %s %s' % (start_dt, end_dt))
            self._end_day = date_to_ts(end_dt)
            self._start_day = date_to_ts(start_dt)

    def get_db_record(self, class_inc, **kwargs):
        return DBSet.get_db_client().select_all(class_inc, **kwargs)

    def get_db_record_names(self, class_inc, **kwargs):
        res = DBSet.get_db_client().iter_all(class_inc, **kwargs)
        names_map = {}
        for obj in res:
            names_map[obj.id] = obj.name
        return names_map

    def get_db_record_name(self, class_inc, **kwargs):
        res = DBSet.get_db_client().select_all(class_inc, **kwargs)
        name = 'unknown'
        if res:
            name = res[0].name
        else:
            reason = ""
            for k, v in kwargs.iteritems():
                reason = "%s:%s " % (k,v)
            name = ('%s-%s')%(name, reason)
        return name

    def set_report_db(self, report_db):
        self._report_db = report_db

    def set_cache_db(self, cache_db):
        self._cache_db = cache_db

    def set_short_cache(self, k, v, expire=settings.redis_mss_in_short_expire):
        if self._cache_db:
            self._cache_db.setex(k, v, expire)

    def set_long_cache(self, k, v, expire=settings.redis_mss_in_long_expire):
        if self._cache_db:
            self._cache_db.setex(k, v, expire)

    def set_cache(self, k, v, ts):
        if self._cur_ts - ts > 2*ONE_DAY_SECONDS:
            self.set_long_cache(k, v)
        else:
            self.set_short_cache(k,v)

    def get_cache(self, k):
        data = None
        if self._cache_db:
            data = self._cache_db.get(k)
            if data:
                data = json.loads(data)
        return data

    def set_sort_default(self, sorts):
        self._sort_default = sorts

    def get_sort_default(self):
        return self._sort_default;

    def get_dict_items(self):
        items = self.get_items()
        result = {}
        for i in xrange(len(items)):
            result[items[i]] = i
        return result

    def set_rules(self, rules):
        self._rules = rules

    def get_rules(self):
        return self._rules

    def is_valid_rules(self, rules):
        for k, v in rules.items():
            _v = self._rules.get(k, None)
            if _v and (_v == IGNORE_RULE_ID or _v == v):
                return True
        return False

    def get_bottom_static(self):
        return []

    def init_data(self):
        pass

    def _init_offer_class(self):
        result = {}
        for _info in AFFILIATE_LIST:
            if _info[0] == 0:
                continue
            res = self.get_db_record(Offer, direct_type=_info[0])
            for obj in res:
                result[obj.id] = obj.direct_offer_id
        return result

    def _init_admin_offer_class(self):
        result = {}
        for _info in AFFILIATE_LIST:
            if _info[0] == 0:
                continue
            res = self.get_db_record(AdminOffer, direct_type=_info[0])
            payouts = self.get_db_record(AdminOfferPayout, uid=self.get_uid())
            for obj in res:
                result[obj.id] = {
                    "nick" : obj.name,
                    "ap" : obj.payout_type,
                    "payout_list" : []
                }
            for obj in payouts:
                if obj.id in result:
                    result[obj.id]["payout_list"].append((obj.payout, obj.start_time, obj.timezone))

        for obj in result.values():
            obj["payout_list"].sort(lambda x,y:cmp(x[1], y[1]))

        return result

    def _match_payout(self, result, ts):
        ap = result["ap"]
        payout_list = result["payout_list"]
        last_payout = ap
        for i in xrange(len(payout_list)):
            payout, start_ts, timezone = payout_list[i]
            diff_ts = (timezone - TIMEZONE) * ONE_HOUR_SECOND
            if ts + diff_ts >= start_ts:
                last_payout = payout
        ap = last_payout
        return ap

    def handle_time_by_timezone(self, time):
        time_str = str(time)
        date = time/100
        hour = time%100
        hour += (self._timezone - TIMEZONE)
        if hour > 23:
            date += 1
        elif hour < 0:
            date -= 1
        hour %= 24
        time = date * 100 + hour
        return time



    def prev_hour_seg_static_result(self, *arg, **argv):
        raise Exception("unimplemented")

    def load_result_with_prev_hour_seg(self, hour=24):
        range_days = self.get_range_days()
        start_day = self.get_start_day()

        if not self.is_origin_timezone():
            self._do_load_first_offset_day(start_day, range_days)
            hour -= self._do_load_last_offset_day(start_day, range_days, save_hour_data=True)
            range_days -= 1

        if self._timezone < TIMEZONE:
            start_day = start_day + ONE_DAY_SECONDS
        while hour > 0 and range_days:
            range_days -= 1
            ts = start_day + range_days*ONE_DAY_SECONDS
            hour -= self.load_part_day(ts, ts, 0, 23, save_hour_data=True)

        if range_days:
            self.load_full_day(start_day, range_days)
        return

    def set_files_path(self, paths):
        self._files_path = paths

    def get_files_path(self):
        return self._files_path

class TotalResult(BaseResult):
    def __init__(self):
        super(TotalResult, self).__init__()
        self.insert_items(['Date'])
        self.add_items(['full_date']);
        self.set_tag('all')
        self.set_sort_default([[0, 'desc']])
        self.finish_init()

    #def load_offset_result(self):
    #    self.load_base_offset_result()

    def static_result(self, datetime_str, key_ts, ts):
        obj = self.get_static_data(datetime_str, datetime_str, key_ts)
        if obj:
            if ts not in self._result_map:
                self._result_map[ts] = (ts, StatResult())
            self._result_map[ts][1].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        result_list = []
        for keys, _info in self._result_map.items():
            _ts, _result = _info
            dt = ts_to_date(_ts)
            datetime_str = dt.strftime('%Y-%m-%d')
            items = _result.to_raw_items()
            items.insert(0, datetime_str)
            items.append(datetime_str)
            result_list.append(items)
        return result_list

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        for keys, _info in self._result_map.items():
            _ts, _result = _info
            total.add(_result)
        items = total.to_raw_items()
        items.insert(0, "Total")
        items.append("")
        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

    def get_raw_custom_data(self, filter_col=None):
        result = {}
        for _key, _info in self._result_map.items():
            _ts, _result = _info
            items = []
            for k in self._custom_head:
                v = getattr(_result, k)
                items.append(v)
            result[_ts] = items
        return result

class CampaignResult(BaseResult):
    def __init__(self):
        super(CampaignResult, self).__init__()
        self.insert_items(['Campaign'])
        self.add_items(['cpid'])
        self.add_json_keys([{"key":"cpid", "class":Campaign, "is_rule":False}])
        self.set_tag('campaign')
        self.set_sort_default([[1, 'desc'], [2, 'desc']])
        self.add_filter_items('Campaign', 'contains')
        self.add_dashboard_head(['Campaign'])
        self.finish_init()

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        for keys, _info in self._result_map.items():
            key_list, _result, _ts  = _info
            total.add(_result)
        items = total.to_raw_items()
        items.insert(0, "Total")
        items.append(-1)
        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

    def get_raw_custom_data(self, filter_col=None):
        result = {}
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            cpid = key_list[0]
            if cpid not in result:
                result[cpid] = {}
            items = []
            for k in self._custom_head:
                v = getattr(_result, k)
                items.append(v)
            result[cpid] = items
        return result

class CampaignDateResult(BaseResult):
    def __init__(self):
        super(CampaignDateResult, self).__init__()
        self.insert_items(['Date', 'Campaign'])
        self.add_items(['cpid'])
        self.add_json_keys([{"key":"cpid", "class":Campaign, "is_rule":False}])
        self.set_tag('campaign')
        self.set_date(True)
        self.set_sort_default([[0, 'desc']])
        self.finish_init()

    def load_offset_result(self):
        self.load_base_offset_result()

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        ret = []
        if objs:
            for obj in objs:
                cpid = obj.get('cpid', None)
                if cpid is not None and self.is_valid_rules({"cpid":cpid}):
                    if ts not in self._result_map:
                        self._result_map[ts] = len(self._result_list)
                        self._result_list.append((ts, cpid, StatResult()))

                    index = self._result_map[ts]
                    self._result_list[index][2].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        raw_list = []
        names_map = self.get_cpnames() or self.get_db_record_names(Campaign, uid=self.get_uid())
        for ts, cpid, _result in self._result_list:
            items = _result.to_raw_items()
            cpid_name = names_map.get(cpid, "%s" % (cpid))
            items.insert(0, cpid_name)
            dt = ts_to_date(ts)
            datetime_str = dt.strftime('%Y-%m-%d')
            items.insert(0, datetime_str)
            items.append(cpid)
            raw_list.append(items)
        return raw_list

class CampaignHourResult(BaseResult):
    def __init__(self):
        super(CampaignHourResult, self).__init__()
        self.insert_items(['Hour', 'Campaign'])
        self.add_items(['cpid'])
        self.add_json_keys([{"key":"cpid", "class":Campaign, "is_rule":False}])
        self.set_tag('campaign')
        self.set_sort_default([[0, 'desc']])
        self.set_data_type(STATIC_DATA_BY_HOUR)
        self.finish_init()
        self._hour_data_key = ['cpid', 'visits', 'clicks', 'conversions']

    def __cal_range_day(self):
        range_days = self.get_range_days()
        days = []
        cnt = 0
        for i in xrange(range_days-1, -1, -1):
            if cnt > 7:
                break
            days.append(i)
            cnt = cnt + 1
        return days

    def get_hour_data(self, obj):
        ret = {}
        for k in self._hour_data_key:
            ret[k] = obj[k]
        return ret

    def load_custom_result(self):
        self.set_full_day(False)
        diff_time = self.get_offset_timezone()
        start_day = self.get_start_day()
        end_day = self.get_end_day()

        ts = start_day
        hours = (end_day - start_day) / 3600
        if hours >= 24:
            hours = 24
        for i in xrange(hours):
            hour_dt = datetime.datetime.fromtimestamp(ts+ i*ONE_HOUR_SECOND)
            datetime_str = hour_dt.strftime('%Y%m%d%H')
            h_ts = date_to_ts(hour_dt)

            diff_dt = datetime.datetime.fromtimestamp(ts+diff_time+ i*ONE_HOUR_SECOND)
            datetime_str = diff_dt.strftime('%Y%m%d%H')
            diff_ts = date_to_ts(diff_dt)
            objs = self.get_static_data(datetime_str, datetime_str, diff_ts)
            if objs:
                for obj in objs:
                    cpid = obj.get('cpid', None)
                    if cpid is not None and self.is_valid_rules({"cpid":cpid}):
                        tmp = StatResult()
                        tmp.from_dict(obj)
                        self._result_list.append((h_ts, cpid, tmp))

    def load_result(self):
        self.set_full_day(False)
        diff_time = self.get_offset_timezone()
        start_day = self.get_start_day() + self._start_hour * ONE_HOUR_SECOND + diff_time
        end_day = self.get_end_day() + self._end_hour * ONE_HOUR_SECOND + diff_time
        hour_data_n = 24
        for hour in xrange(start_day, end_day+ONE_HOUR_SECOND, ONE_HOUR_SECOND):
            hour_dt = datetime.datetime.fromtimestamp(hour)
            datetime_str = hour_dt.strftime('%Y%m%d%H')
            objs = self.get_static_data(datetime_str, datetime_str, hour)
            if objs:
                for obj in objs:
                    cpid = obj.get('cpid', None)
                    if cpid is not None and self.is_valid_rules({"cpid":cpid}):
                        tmp = StatResult()
                        tmp.from_dict(obj)
                        self._result_list.append((hour-diff_time, cpid, tmp))
                        self._hour_data[int(datetime_str)] = self.get_hour_data(obj)

    def load_result2(self):
        self.set_full_day(False)
        diff_time = self.get_offset_timezone()
        start_day = self.get_start_day()
        days = self.__cal_range_day()
        hour_data_n = 24
        for i in days:
            cur_dt = datetime.datetime.fromtimestamp(start_day+ i*ONE_DAY_SECONDS)
            ts = date_to_ts(cur_dt)
            for j in xrange(24):
                hour_dt = datetime.datetime.fromtimestamp(ts+ j*ONE_HOUR_SECOND)
                datetime_str = hour_dt.strftime('%Y%m%d%H')
                h_ts = date_to_ts(hour_dt)

                diff_dt = datetime.datetime.fromtimestamp(ts+diff_time+ j*ONE_HOUR_SECOND)
                datetime_str = diff_dt.strftime('%Y%m%d%H')
                diff_ts = date_to_ts(diff_dt)
                objs = self.get_static_data(datetime_str, datetime_str, diff_ts)
                if objs:
                    for obj in objs:
                        cpid = obj.get('cpid', None)
                        if cpid is not None and self.is_valid_rules({"cpid":cpid}):
                            tmp = StatResult()
                            tmp.from_dict(obj)
                            self._result_list.append((h_ts, cpid, tmp))
                            self._hour_data[int(datetime_str)] = self.get_hour_data(obj)

    def get_raw_data(self, filter_col=None):
        raw_list = []
        names_map = self.get_cpnames() or self.get_db_record_names(Campaign, uid=self.get_uid())
        for ts, cpid, _result in self._result_list:
            items = _result.to_raw_items()
            cpid_name = names_map.get(cpid, "%s" % (cpid))
            items.insert(0, cpid_name)
            dt = ts_to_date(ts)
            datetime_str = dt.strftime('%Y%m%d %H:00')
            items.insert(0, datetime_str[4:])
            items.append(cpid)
            raw_list.append(items)
        return raw_list

    def get_raw_custom_data(self, filter_col=None):
        result = {}
        for ts, cpid, _result in self._result_list:
            if cpid not in result:
                result[cpid] = {}
            if ts not in result[cpid]:
                result[cpid][ts] = []
            items = []
            for k in self._custom_head:
                v = getattr(_result, k)
                items.append(v)
            result[cpid][ts] = items
        return result

    def get_kendo_charts(self):
        return self.handle_hour_data()

    def handle_hour_data(self):
        if not self._hour_data:
            return {'charts': []}
        rules = self.get_rules()
        camp = DBSet.get_db_client().select_one(Campaign, id=rules['cpid'])
        cpname = camp.name if camp else str(rules['cid'])

        time_list = sorted(self._hour_data.keys())
        time_dict = {}
        for t in time_list:
            time_dict[t] = self.handle_time_by_timezone(t)

        data = []
        for time_str in time_list:
            val = self._hour_data[time_str]
            data.append({"value":val['clicks'], 'time':time_str, 'name':"clicks"})
            data.append({"value":val['conversions'], 'time':time_str, 'name':"convs"})
            data.append({"value":val['visits'], 'time':time_str, 'name':"visits"})

        sort = {'field':"time", 'dir':'asc'}
        ret = {
            'charts':[
                {'name':'convs', 'title': cpname, 'data': data, 'sort':sort},
            ]
        }
        return ret



class PathResult(BaseResult):
    def __init__(self):
        super(PathResult, self).__init__()
        self.insert_items(['Campaign', 'Path'])
        self.add_items(['cpid', 'pid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"pid", "class":Path, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('path')
        self.set_sort_default([[0,'asc'],[2, 'desc'],[3, 'desc']])
        self.add_filter_items('Path', 'contains')
        self.finish_init()

class WebsiteResult(BaseResult):
    def __init__(self):
        super(WebsiteResult, self).__init__()
        self.insert_items(['Campaign', 'Website'])
        self.add_items(['cpid', 'websiteid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"websiteid", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('websiteid')
        self.set_sort_default([[0,'asc'],[2, 'desc'],[3, 'desc']])
        self.add_filter_items('Website', 'contains')
        self.set_tar_prefix_name("websiteid_")
        self.finish_init()

    def set_rules(self, rules):
        super(WebsiteResult, self).set_rules(rules)
        cpid = rules.get("cpid", 0)
        prefix_name = "websiteid_%s_" % cpid
        self.set_tar_prefix_name(prefix_name)

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        result_list = []
        is_crypt = self.is_crypt_user()
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()
            for i in range(len(key_list)-1, -1,-1):
                k = key_list[i]
                jk_k = self._json_keys[i].get("key", None)
                if is_crypt:
                    if jk_k == "websiteid" and str(k) != "":
                        k = self.crypto(str(k))
                if jk_k and jk_k in names_map:
                    name = names_map[jk_k].get(k, "%s"%k)
                    items.insert(0, name)
                else:
                    items.insert(0, k)
            if self._is_show_date:
                dt = ts_to_date(ts)
                datetime_str = dt.strftime('%Y%m%d')
                items = _result.to_raw_items()
                items.insert(0, datetime_str[4:])

            for i in xrange(len(key_list)):
                if self._json_keys[i].get("add_ignore", None):
                    continue
                k = key_list[i]
                items.append(k)
            if filter_col:
                filter_items = []
                for col in filter_col:
                    filter_items.append(items[col])
                items = filter_items
            result_list.append(items)
        return result_list


class LandPageResult(BaseResult):
    def __init__(self):
        super(LandPageResult, self).__init__()
        self.insert_items(['Campaign', 'Landerpage'])
        self.add_items(['cpid', 'lpid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"lpid", "class":LandingPage, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('landing_page')
        self.set_sort_default([[0,'asc'],[2, 'desc'],[3, 'desc']])
        self.add_filter_items('Landerpage', 'contains')
        self.finish_init()

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        result_list = []
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()
            items[6] = 0.0
            for i in range(len(key_list)-1, -1,-1):
                k = key_list[i]
                jk_k = self._json_keys[i].get("key", None)
                if jk_k and jk_k in names_map:
                    name = names_map[jk_k].get(k, "%s"%k)
                    items.insert(0, name)
                else:
                    items.insert(0, k)
            if self._is_show_date:
                dt = ts_to_date(ts)
                datetime_str = dt.strftime('%Y%m%d')
                items = _result.to_raw_items()
                items.insert(0, datetime_str[4:])

            for i in xrange(len(key_list)):
                if self._json_keys[i].get("add_ignore", None):
                    continue
                k = key_list[i]
                items.append(k)
            if filter_col:
                filter_items = []
                for col in filter_col:
                    filter_items.append(items[col])
                items = filter_items
            result_list.append(items)
        return result_list

class OfferResult(BaseResult):
    def __init__(self):
        super(OfferResult, self).__init__()
        self.insert_items(['Campaign', 'Offer'])
        self.add_items(['cpid', 'oid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"oid", "class":Offer, "is_rule":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('offer')
        self.set_sort_default([[0,'asc'],[2, 'desc'],[3, 'desc']])
        self.add_filter_items('Offer', 'contains')
        self.add_filter_items('Convs', 'lt')
        self.add_filter_items('Clicks', 'lt')
        self.add_dashboard_head(['Offer'])
        self._hour_data_key = ['cpid', 'oid', 'clicks', 'conversions']
        self.finish_init()

    def get_kendo_data(self):
        ret = super(OfferResult, self).get_kendo_data()
        return ret

    def get_kendo_charts(self):
        return self.handle_hour_data()

    def handle_hour_data(self):
        if not self._hour_data:
            return {'charts': []}
        cpid_names_map = self.get_cpnames() or self.get_db_record_names(Campaign, uid=self.get_uid())
        tmp = {}
        n = False
        for k, v in self._hour_data.items():
            for i in v:
                if not n:
                    n = True
                name = cpid_names_map.get(i['cpid'], str(i['cpid']))
                if name not in tmp:
                    tmp[name] = {}
                tmp[name][k] = i
        time_list = sorted(self._hour_data.keys())

        visits = []
        convs = []
        v_total = [0] * len(time_list)
        c_total = [0] * len(time_list)
        time_dict = {}
        for t in time_list:
            time_dict[t] = self.handle_time_by_timezone(t)

        for cpname, v in tmp.items():
            n = 0
            for time_str in time_list:
                val = v.get(time_str)
                if val is None:
                    conv_data = 0
                    visit_data = 0
                else:
                    conv_data = val['conversions']
                    visit_data = val['clicks']
                v_total[n] += visit_data
                c_total[n] += conv_data
                visits.append({'name': cpname, 'value':visit_data, 'time':time_dict[time_str]})
                convs.append({'name': cpname, 'value':conv_data, 'time':time_dict[time_str]})
                n += 1

        sort = {'field':"time", 'dir':'asc'}
        v_total = self.list_to_record(v_total, time_list)
        c_total = self.list_to_record(c_total, time_list)
        visits.extend(v_total)
        convs.extend(c_total)
        rules = self.get_rules()
        offer = DBSet.get_db_client().select_one(Offer, id=rules['oid'])
        name = offer.name if offer else rules['oid']
        items = tmp.keys()
        items.append("Total")
        ret = {
            'charts':[
                {'name':'click', 'data': visits, 'title':'%s clicks'%name, 'sort':sort},
                {'name':'convs', 'title':'%s convs'%name, 'data': convs, 'sort':sort},
            ],
            'items': [{'text': cpname} for cpname in items]
        }
        return ret

    def list_to_record(self, l, time_list):
        n = 0
        ret = []
        while n < len(l):
            rec = {'value':l[n], 'name': 'Total', 'time':time_list[n]}
            ret.append(rec)
            n += 1
        return ret

    def prev_hour_seg_static_result(self, datetime_str, k_ts, ts):
        json_keys = self._json_keys
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        ret = []
        if objs:
            for obj in objs:
                res = self.check_is_valid(obj, json_keys)
                if not res["ok"]:
                    continue
                if self._is_show_date:
                    keys = ts
                else:
                    keys = "-".join([str(s) for s in res["key_list"]])
                if keys not in self._result_map:
                    tmp = StatResult()
                    self._result_map[keys] = (res["key_list"], tmp, ts)
                self._result_map[keys][1].add_raw(obj)
                ret.append(self.get_hour_data(obj))
            return ret
        return None

    def get_hour_data(self, obj):
        ret = {}
        for k in self._hour_data_key:
            ret[k] = obj[k]
        return ret

    def load_result(self):
        if self.get_rules().get("oid") <= 0:
            super(OfferResult, self).load_result()
        else:
            self.load_result_with_prev_hour_seg()
            keys = sorted(self._hour_data.keys(), reverse=True)[:24]
            hour_data = {}
            for k in keys:
                hour_data[k] = self._hour_data[k]
            self._hour_data = hour_data

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        result_list = []
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()
            items[6] = 0.0
            for i in range(len(key_list)-1, -1,-1):
                k = key_list[i]
                jk_k = self._json_keys[i].get("key", None)
                if jk_k and jk_k in names_map:
                    name = names_map[jk_k].get(k, "%s"%k)
                    items.insert(0, name)
                else:
                    items.insert(0, k)
            if self._is_show_date:
                dt = ts_to_date(ts)
                datetime_str = dt.strftime('%Y%m%d')
                items = _result.to_raw_items()
                items.insert(0, datetime_str[4:])

            for i in xrange(len(key_list)):
                if self._json_keys[i].get("add_ignore", None):
                    continue
                k = key_list[i]
                items.append(k)
            if filter_col:
                filter_items = []
                for col in filter_col:
                    filter_items.append(items[col])
                items = filter_items
            result_list.append(items)
        return result_list

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        for keys, _info in self._result_map.items():
            key_list, _result, _ts  = _info
            total.add(_result)
        items = total.to_raw_items()
        items.insert(0, "Total")
        items.append(-1)
        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

class AffiliateNetworkResult(BaseResult):
    def __init__(self):
        super(AffiliateNetworkResult, self).__init__()
        self.insert_items(['Network'])
        self.add_items(['nid'])
        #json_keys = [
        #    {"key":"nid", "class":AffiliateNetwork, "is_rule":False},
        #]
        #self.add_json_keys(json_keys)
        self.set_tag('network')
        self.set_sort_default([[1, 'desc']])
        self.add_filter_items('Network', 'contains')
        self.finish_init()

    def set_uid(self, uid):
        super(AffiliateNetworkResult, self).set_uid(uid)
        if not self.check_is_inner_user(self._raw_uid):
            cls = AffiliateNetwork
            json_keys = [
                {"key":"nid", "class":cls, "is_rule":False},
            ]
        else:
            cls = AdminAffiliateNetwork
            json_keys = [
                {"key":"nid", "class":cls, "is_rule":False, "admin_uid" : 1},
            ]
        self.add_json_keys(json_keys)

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        for keys, _info in self._result_map.items():
            key_list, _result, _ts  = _info
            total.add(_result)
        items = total.to_raw_items()
        items.insert(0, "Total")
        items.append(-1)
        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

class TrafficSourceResult(BaseResult):
    def __init__(self):
        super(TrafficSourceResult, self).__init__()
        self.insert_items(['TrafficeSource'])
        self.add_items(['tsid'])
        #json_keys = [
        #    {"key":"tsid", "class":TrafficSource, "is_rule":False},
        #]
        #self.add_json_keys(json_keys)
        self.set_tag('traffic_source')
        self.set_sort_default([[1, 'desc']])
        self.add_filter_items('TrafficeSource', 'contains')
        self.add_dashboard_head(['TrafficeSource'])
        self.finish_init()

    def set_uid(self, uid):
        super(TrafficSourceResult, self).set_uid(uid)
        if not self.check_is_inner_user(self._raw_uid):
            cls = TrafficSource
            json_keys = [
                {"key":"tsid", "class":cls, "is_rule":False},
            ]
        else:
            cls = AdminTrafficSource
            json_keys = [
                {"key":"tsid", "class":cls, "is_rule":False, "admin_uid" : 1},
            ]
        self.add_json_keys(json_keys)

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        for keys, _info in self._result_map.items():
            key_list, _result, _ts  = _info
            total.add(_result)
        items = total.to_raw_items()
        items.insert(0, "Total")
        items.append(-1)
        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

class IspResult(BaseResult):
    def __init__(self):
        super(IspResult, self).__init__()
        self.insert_items(['Campaign', 'ISP'])
        self.add_items(['cpid', 'isp'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"isp", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('isp')
        self.set_sort_default([[2, 'desc']])
        self.add_filter_items('ISP', 'contains')
        self.finish_init()

class BrowserResult(BaseResult):
    def __init__(self):
        super(BrowserResult, self).__init__()
        self.insert_items(['Campaign', 'Browser'])
        self.add_items(['cpid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"browser", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('browser')
        self.set_sort_default([[2, 'desc']])
        self.add_filter_items('Browser', 'contains')
        self.finish_init()

class OSResult(BaseResult):
    def __init__(self):
        super(OSResult, self).__init__()
        self.insert_items(['Campaign', 'OS'])
        self.add_items(['cpid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"os", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('os')
        self.set_sort_default([[2, 'desc']])
        self.add_filter_items('OS', 'contains')
        self.finish_init()

class CountryResult(BaseResult):
    def __init__(self):
        super(CountryResult, self).__init__()
        self.insert_items(['Campaign', 'Country'])
        self.add_items(['cpid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"country", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('country')
        self.set_sort_default([[2, 'desc']])
        self.add_filter_items('Country', 'contains')
        self.finish_init()

class CountryIspResult(BaseResult):
    def __init__(self):
        super(CountryIspResult, self).__init__()
        self.insert_items(['Campaign', 'Country', 'ISP'])
        self.add_items(['cpid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"country_isp", "class":None, "is_rule":False, "add_ignore":True},
            #{"key":"isp", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('country_isp')
        self.set_sort_default([[3, 'desc'], [1,'desc']])
        self.add_filter_items('Country', 'contains')
        self.add_filter_items('ISP', 'contains')
        self.set_tar_prefix_name('countryisp_')
        self.finish_init()

    def _do_static_result(self, obj, ts):
        res = self.check_is_valid(obj, self._json_keys)
        if not res["ok"]:
           return False

        keys = "-".join([str(s) for s in res["key_list"]])
        if keys not in self._result_map:
            tmp = StatResult()
            self._result_map[keys] = (res["key_list"], tmp, ts)
        self._result_map[keys][1].add_raw(obj)
        return True

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            cpid = self._rules.get("cpid", -1)
            if int(cpid) == -1:
                return
            if type(objs) == dict:
                for _isp, _info in objs.items():
                    obj = _info.get(unicode(cpid), None)
                    if obj is None:
                        continue
                    if not self._do_static_result(obj, ts):
                        continue
            elif type(objs) == list:
                for obj in objs:
                    if not self._do_static_result(obj, ts):
                        continue

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        result_list = []
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()
            #country isp
            _list = key_list[1].split("_")
            items.insert(0, _list[1])
            items.insert(0, _list[0])

            #campaign
            cp_key = key_list[0]
            cp_name = ""
            jk_k = self._json_keys[0].get("key", None)
            if jk_k and jk_k in names_map:
                cp_name = names_map[jk_k].get(cp_key, "%s"%cp_key)
            else:
                cp_name = cp_key
            items.insert(0, cp_name)

            for i in xrange(len(key_list)):
                if self._json_keys[i].get("add_ignore", None):
                    continue
                k = key_list[i]
                items.append(k)

            if filter_col:
                filter_items = []
                for col in filter_col:
                    filter_items.append(items[col])
                items = filter_items
            result_list.append(items)
        return result_list

class DomainResult(BaseResult):
    def __init__(self):
        super(DomainResult, self).__init__()
        self.insert_items(['Campaign', 'Domain'])
        self.add_items(['cpid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"domain", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('domain')
        self.set_sort_default([[2, 'desc']])
        self.add_filter_items('Domain', 'contains')
        self.finish_init()

class RefResult(BaseResult):
    def __init__(self):
        super(RefResult, self).__init__()
        self.insert_items(['Campaign', 'Referrer'])
        self.add_items(['cpid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"ref", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('ref')
        self.set_sort_default([[2, 'desc']])
        self.set_tar_prefix_name('referrer_')
        self.finish_init()

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        result_list = []
        is_crypt = self.is_crypt_user()
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()
            for i in range(len(key_list)-1, -1,-1):
                k = key_list[i]
                jk_k = self._json_keys[i].get("key", None)
                if is_crypt:
                    if jk_k == "ref" and str(k) != "":
                        k = self.crypto(str(k))
                if jk_k and jk_k in names_map:
                    name = names_map[jk_k].get(k, "%s"%k)
                    items.insert(0, name)
                else:
                    items.insert(0, k)
            if self._is_show_date:
                dt = ts_to_date(ts)
                datetime_str = dt.strftime('%Y%m%d')
                items = _result.to_raw_items()
                items.insert(0, datetime_str[4:])

            for i in xrange(len(key_list)):
                if self._json_keys[i].get("add_ignore", None):
                    continue
                k = key_list[i]
                items.append(k)
            if filter_col:
                filter_items = []
                for col in filter_col:
                    filter_items.append(items[col])
                items = filter_items
            result_list.append(items)
        return result_list

class LanderRefResult(BaseResult):
    def __init__(self):
        super(LanderRefResult, self).__init__()
        items = ['Campaign', 'Referrer', 'cloak']
        self.set_items(items)
        self.add_items(['cpid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"ref", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('lander_ref')
        self.set_sort_default([[2, 'desc']])
        self.add_filter_items('Referrer', 'contains')
        self.set_tar_prefix_name('referrer_')
        self.finish_init()

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if not objs:
            return
        for obj in objs:
            cpid = obj.get('cpid', None)
            ref = obj.get('ref', None)
            if cpid is not None and ref is not None and self.is_valid_rules({"cpid":cpid}):
                count = obj.get('count', None)
                if cpid not in self._result_map:
                    self._result_map[cpid] = {}
                if ref not in self._result_map[cpid]:
                    self._result_map[cpid][ref] = len(self._result_list)
                    self._result_list.append((cpid, ref, count))
                else:
                    idx = self._result_map[cpid][ref]
                    cpid, ref, _count = self._result_list[idx]
                    self._result_list[idx] = (cpid, ref, count + _count)

    def get_raw_data(self, filter_col=None):
        raw_list = []
        is_crypt = self.is_crypt_user()
        cpid_names_map = self.get_cpnames() or self.get_db_record_names(Campaign, uid=self.get_uid())
        for cpid, ref, count in self._result_list:
            cpid_name = cpid_names_map.get(cpid, "%s" % (cpid))
            if is_crypt and ref != "":
                ref = self.crypto(ref)
            items = [cpid_name, ref, count, cpid]
            raw_list.append(items)
        return raw_list

    def get_raw_custom_data(self, filter_col=None):
        result = {}
        for cpid, ref, count in self._result_list:
            if cpid not in result:
                result[cpid] = {}
            items = [ref, count]
            result[cpid] = items
        return result

class TsRefResult(BaseResult):
    def __init__(self):
        super(TsRefResult, self).__init__()
        items = ['Campaign', 'Referrer', 'cloak_ts']
        self.set_items(items)
        self.add_items(['cpid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"ref", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('ts_ref')
        self.set_sort_default([[2, 'desc']])
        self.add_filter_items('Referrer', 'contains')
        self.set_tar_prefix_name('referrer_')
        self.finish_init()

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if not objs:
            return
        for obj in objs:
            cpid = obj.get('cpid', None)
            ref = obj.get('ref', None)
            if cpid is not None and ref is not None and self.is_valid_rules({"cpid":cpid}):
                count = obj.get('count', None)
                if cpid not in self._result_map:
                    self._result_map[cpid] = {}
                if ref not in self._result_map[cpid]:
                    self._result_map[cpid][ref] = len(self._result_list)
                    self._result_list.append((cpid, ref, count))
                else:
                    idx = self._result_map[cpid][ref]
                    cpid, ref, _count = self._result_list[idx]
                    self._result_list[idx] = (cpid, ref, count + _count)

    def get_raw_data(self, filter_col=None):
        raw_list = []
        is_crypt = self.is_crypt_user()
        cpid_names_map = self.get_cpnames() or self.get_db_record_names(Campaign, uid=self.get_uid())
        for cpid, ref, count in self._result_list:
            cpid_name = cpid_names_map.get(cpid, "%s" % (cpid))
            if is_crypt  and ref != "":
                ref = self.crypto(ref)
            items = [cpid_name, ref, count, cpid]
            raw_list.append(items)
        return raw_list

    def get_raw_custom_data(self, filter_col=None):
        result = {}
        for cpid, ref, count in self._result_list:
            if cpid not in result:
                result[cpid] = {}
            items = [ref, count]
            result[cpid] = items
        return result

class AdminBillResult(BaseResult):
    def __init__(self):
        super(AdminBillResult, self).__init__()
        self._dettail_items = []
        self._normal_items = []
        items = ['User', 'Date', 'Visits', 'Clicks', 'Convs', 'Warns', 'Tracks', 'Price', 'TrackCost', 'Flow', 'FlowCost', 'TotalCost', 'FlowDetail']
        self.set_items(items)
        self.set_normal_items(['User', 'Date', 'Tracks', 'Price', 'TrackCost', 'Flow', 'FlowCost', 'TotalCost'])
        self.set_detail_items(['Tracks', 'Visits', 'Clicks', 'Convs', 'Warns'])
        items = ['Date', 'Visits', 'Clicks', 'Convs', 'Revenue', 'Cost', 'Profit']
        self.set_dashboard_chart_items(items)
        self.set_tag('all')
        self.set_sort_default([[0, 'desc']])
        self.add_filter_items('User', 'contains')
        self.finish_init()

    def __get_flow_data_file_path(self, file_name):
        file_name = self.get_file_flow_full_name(file_name)
        path = osp.join(settings.flow_data_dir, str(self.get_uid()))
        path = osp.join(path, file_name)
        return path

    def get_file_flow_full_name(self, file_name):
        return  "%s.flow" % file_name

    def get_file_flow_static_data(self, file_name, k, ts):
        key = self.get_mss_db_key(k)
        data = self.get_cache(key)
        file_path = self.__get_flow_data_file_path(file_name)
        if data is None or self.check_file_is_modify(file_path, file_name):
            obj = self.get_static_data_from_file(file_path)
            if obj:
                data = obj
                self._set_data_cache(obj, file_name, ts)
        data = data if data else {}
        return data

    def get_all_uids(self):
        res = DBSet.get_db_client().iter_all(User)
        uids = []
        for obj in res:
            uids.append((obj.id, obj.name))
        return uids

    def load_result(self):
        uids = self.get_all_uids()
        for info in uids:
            uid, name = info
            self.set_uid(uid)
            self.set_user_name(name)
            super(AdminBillResult, self).load_result()

    def get_flow_static_data(self, file_name, key, ts):
        return self.get_file_flow_static_data(file_name, key, ts)

    def static_result(self, datetime_str, k_ts, ts):
        obj = self.get_static_data(datetime_str, datetime_str, k_ts)
        flow_obj = self.get_flow_static_data(datetime_str, datetime_str, k_ts)
        user_name = self.get_user_name()
        if obj or flow_obj:
            if user_name not in self._result_map:
                self._result_map[user_name] = {}
            if ts not in self._result_map[user_name]:
                self._result_map[user_name][ts] = (ts, StatResult(), flow_obj)
            if obj:
                self._result_map[user_name][ts][1].add_raw(obj)

    def get_help_tips(self):
        return FLOW_HELP_TIPS

    def set_detail_items(self, items):
        self._dettail_items = items

    def get_detail_items(self):
        return self._dettail_items

    def set_normal_items(self, items):
        self._normal_items = items

    def get_normal_items(self):
        return self._normal_items

    def get_kendo_data(self):
        result = super(AdminBillResult, self).get_kendo_data()
        result['normal_field'] = self.get_normal_items()
        result['detail_field'] = self.get_detail_items()
        result['areas'] = FLOW_AREAS
        return result

    def get_raw_data(self, filter_col=None):
        result_list = []
        price = settings.massival_common_price
        for user_name, v in self._result_map.items():
            for key, _info in v.items():
                _ts, _result, _flow = _info
                flow_total = 0
                flow_cost = 0
                flow_detail = {}
                if _flow:
                    for area, _flow_data in _flow.items():
                        upload = _flow_data[0]/1024.0/1024/1024
                        download = _flow_data[1]/1024.0/1024/1024
                        flow_detail[area] = [upload, download]
                        flow_total += upload + download
                        flow_cost += (upload + download) * FLOW_PRICE[area]

                dt = ts_to_date(_ts)
                datetime_str = dt.strftime('%Y%m%d')
                total = _result.visits + _result.clicks + _result.conversions + _result.warns
                items = []
                items.append(user_name)
                items.append(datetime_str[4:])
                items.append(_result.visits)
                items.append(_result.clicks)
                items.append(_result.conversions)
                items.append(_result.warns)
                items.append(total)
                items.append(price)
                items.append(total * price / 1000)
                items.append(flow_total)
                items.append(flow_cost)
                items.append(total * price / 1000 + flow_cost)
                items.append(flow_detail)
                result_list.append(items)
        return result_list

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        flow_total = 0
        flow_cost = 0
        flow_detail = {}
        price = settings.massival_common_price
        for user_name, v in self._result_map.items():
            for key, _info in v.items():
                _ts, _result, _flow = _info
                for area, _flow_data in _flow.items():
                    upload = _flow_data[0]/1024.0/1024/1024
                    download = _flow_data[1]/1024.0/1024/1024
                    flow_total += upload + download
                    if flow_detail.get(area, None) is None:
                        flow_detail[area] = 0
                    flow_detail[area] += upload + download
                    flow_cost += (upload + download) * FLOW_PRICE[area]
                total.add(_result)
        items = []
        all = total.visits + total.clicks + total.conversions + total.warns
        items.append("Total")
        items.append("")
        items.append(total.visits)
        items.append(total.clicks)
        items.append(total.conversions)
        items.append(total.warns)
        items.append(all)
        items.append(price)
        items.append(all* price / 1000)
        items.append(0)
        items.append(flow_cost)
        items.append(all* price / 1000 + flow_cost)
        items.append(0)

        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

    def load_chart_result(self):
        range_days = self.get_range_days()
        start_day = self.get_start_day()
        for i in xrange(range_days):
            cur_dt = datetime.datetime.fromtimestamp(start_day + i*ONE_DAY_SECONDS)
            datetime_str = cur_dt.strftime('%Y%m%d')
            ts = date_to_ts(cur_dt)
            obj = self.get_static_data(datetime_str, datetime_str, ts)
            if obj:
                tmp_result = StatResult()
                tmp_result.from_dict(obj)
                self._result_list.append((ts, tmp_result))
            else:
                self._result_list.append((ts, StatResult()))

    def __min(self, a, b, c, m):
        t = min(a,b)
        t = min(t,c)
        if m is not None:
            return min(m, t)
        else:
            return t

    def __max(self, a, b, c, m):
        t = max(a,b)
        t = max(t,c)
        if m is not None:
            return max(t, m)
        else:
            return t

    def get_chart_data(self):
        def check_none(a):
            if a is None:
                return 0
            return a
        result_list = []
        min_count = 0
        max_count = 100
        min_cash = -50
        max_cash = 50
        for _ts, _result in self._result_list:
            dt = ts_to_date(_ts)
            datetime_str = dt.strftime('%m/%d/%Y')
            items = []
            items.append(datetime_str)
            items.append(_result.visits)
            items.append(_result.clicks)
            items.append(_result.conversions)
            items.append(_result.revenue)
            items.append(_result.cost)
            items.append(_result.profit)
            items.append(_result.ROI)
            result_list.append(items)
            min_count = self.__min(_result.visits, _result.clicks, _result.conversions, min_count)
            max_count = self.__max(_result.visits, _result.clicks, _result.conversions, max_count)
            min_cash = self.__min(_result.profit, _result.revenue, _result.cost, min_cash)
            max_cash = self.__max(_result.profit, _result.revenue, _result.cost, max_cash)

        min_count = check_none(min_count)
        max_count = check_none(max_count)
        min_cash = check_none(min_cash)
        max_cash = check_none(max_cash)
        axis = {
            "count" : [min_count, max_count],
            #"cash" : [min_count, max_count],
            "cash" : [min_cash, max_cash],
        }
        return {
            "datas" : result_list,
            "axis" : axis,
        }

    def get_total_static(self):
        items = ['Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'ROI']
        result = []
        total = StatResult()
        for _ts, _result in self._result_list:
            total.add(_result)

        result.append(format_int_comma(total.visits, ","))
        result.append(format_int_comma(total.clicks, ","))
        result.append(format_int_comma(total.conversions, ","))
        result.append('$%s'%(format_float_comma(float('%0.2f'%total.profit),",")))
        result.append('$%s'%(format_float_comma(float('%0.2f'%total.revenue),",")))
        result.append('$%s'%(format_float_comma(float('%0.2f'%total.cost),",")))
        result.append('%0.2f%%'%total.ROI)
        return result, items



class BillResult(BaseResult):
    def __init__(self):
        super(BillResult, self).__init__()
        self._dettail_items = []
        self._normal_items = []
        items = ['Date', 'Visits', 'Clicks', 'Convs', 'Warns', 'Tracks', 'Price', 'TrackCost', 'Flow', 'FlowCost', 'TotalCost', 'FlowDetail']
        self.set_items(items)
        self.set_normal_items(['Date', 'Tracks', 'Price', 'TrackCost', 'Flow', 'FlowCost', 'TotalCost'])
        self.set_detail_items(['Tracks', 'Visits', 'Clicks', 'Convs', 'Warns'])
        items = ['Date', 'Visits', 'Clicks', 'Convs', 'Revenue', 'Cost', 'Profit']
        self.set_dashboard_chart_items(items)
        self.set_tag('all')
        self.set_sort_default([[0, 'desc']])
        self.finish_init()

    def __get_flow_data_file_path(self, file_name):
        file_name = self.get_file_flow_full_name(file_name)
        path = osp.join(settings.flow_data_dir, str(self.get_uid()))
        path = osp.join(path, file_name)
        return path

    def get_file_flow_full_name(self, file_name):
        return  "%s.flow" % file_name

    def get_file_flow_static_data(self, file_name, k, ts):
        key = self.get_mss_db_key(k)
        data = self.get_cache(key)
        file_path = self.__get_flow_data_file_path(file_name)
        if data is None or self.check_file_is_modify(file_path, file_name):
            obj = self.get_static_data_from_file(file_path)
            if obj:
                data = obj
                self._set_data_cache(obj, file_name, ts)
        data = data if data else {}
        return data

    def get_flow_static_data(self, file_name, key, ts):
        return self.get_file_flow_static_data(file_name, key, ts)

    def static_result(self, datetime_str, k_ts, ts):
        obj = self.get_static_data(datetime_str, datetime_str, k_ts)
        flow_obj = self.get_flow_static_data(datetime_str, datetime_str, k_ts)
        if obj or flow_obj:
            if ts not in self._result_map:
                self._result_map[ts] = (ts, StatResult(), flow_obj)
            if obj:
                self._result_map[ts][1].add_raw(obj)

    def get_help_tips(self):
        return FLOW_HELP_TIPS

    def set_detail_items(self, items):
        self._dettail_items = items

    def get_detail_items(self):
        return self._dettail_items

    def set_normal_items(self, items):
        self._normal_items = items

    def get_normal_items(self):
        return self._normal_items

    def get_kendo_data(self):
        result = super(BillResult, self).get_kendo_data()
        result['normal_field'] = self.get_normal_items()
        result['detail_field'] = self.get_detail_items()
        result['areas'] = FLOW_AREAS
        return result

    def get_raw_data(self, filter_col=None):
        result_list = []
        price = settings.massival_common_price
        for key, _info in self._result_map.items():
            _ts, _result, _flow = _info
            flow_total = 0
            flow_cost = 0
            flow_detail = {}
            if _flow:
                for area, _flow_data in _flow.items():
                    upload = _flow_data[0]/1024.0/1024/1024
                    download = _flow_data[1]/1024.0/1024/1024
                    flow_detail[area] = [upload, download]
                    flow_total += upload + download
                    flow_cost += (upload + download) * FLOW_PRICE[area]

            dt = ts_to_date(_ts)
            datetime_str = dt.strftime('%Y%m%d')
            total = _result.visits + _result.clicks + _result.conversions + _result.warns
            items = []
            items.append(datetime_str[4:])
            items.append(_result.visits)
            items.append(_result.clicks)
            items.append(_result.conversions)
            items.append(_result.warns)
            items.append(total)
            items.append(price)
            items.append(total * price / 1000)
            items.append(flow_total)
            items.append(flow_cost)
            items.append(total * price / 1000 + flow_cost)
            items.append(flow_detail)
            result_list.append(items)
        return result_list

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        flow_total = 0
        flow_cost = 0
        flow_detail = {}
        price = settings.massival_common_price
        for key, _info in self._result_map.items():
            _ts, _result, _flow = _info
            for area, _flow_data in _flow.items():
                upload = _flow_data[0]/1024.0/1024/1024
                download = _flow_data[1]/1024.0/1024/1024
                flow_total += upload + download
                if flow_detail.get(area, None) is None:
                    flow_detail[area] = 0
                flow_detail[area] += upload + download
                flow_cost += (upload + download) * FLOW_PRICE[area]
            total.add(_result)
        items = []
        all = total.visits + total.clicks + total.conversions + total.warns
        items.insert(0, "Total")
        items.append(total.visits)
        items.append(total.clicks)
        items.append(total.conversions)
        items.append(total.warns)
        items.append(all)
        items.append(price)
        items.append(all* price / 1000)
        items.append(0)
        items.append(flow_cost)
        items.append(all* price / 1000 + flow_cost)
        items.append(0)

        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

    def load_chart_result(self):
        range_days = self.get_range_days()
        start_day = self.get_start_day()
        for i in xrange(range_days):
            cur_dt = datetime.datetime.fromtimestamp(start_day + i*ONE_DAY_SECONDS)
            datetime_str = cur_dt.strftime('%Y%m%d')
            ts = date_to_ts(cur_dt)
            obj = self.get_static_data(datetime_str, datetime_str, ts)
            if obj:
                tmp_result = StatResult()
                tmp_result.from_dict(obj)
                self._result_list.append((ts, tmp_result))
            else:
                self._result_list.append((ts, StatResult()))

    def __min(self, a, b, c, m):
        t = min(a,b)
        t = min(t,c)
        if m is not None:
            return min(m, t)
        else:
            return t

    def __max(self, a, b, c, m):
        t = max(a,b)
        t = max(t,c)
        if m is not None:
            return max(t, m)
        else:
            return t

    def get_chart_data(self):
        def check_none(a):
            if a is None:
                return 0
            return a
        result_list = []
        min_count = 0
        max_count = 100
        min_cash = -50
        max_cash = 50
        for _ts, _result in self._result_list:
            dt = ts_to_date(_ts)
            datetime_str = dt.strftime('%m/%d/%Y')
            items = []
            items.append(datetime_str)
            items.append(_result.visits)
            items.append(_result.clicks)
            items.append(_result.conversions)
            items.append(_result.revenue)
            items.append(_result.cost)
            items.append(_result.profit)
            items.append(_result.ROI)
            result_list.append(items)
            min_count = self.__min(_result.visits, _result.clicks, _result.conversions, min_count)
            max_count = self.__max(_result.visits, _result.clicks, _result.conversions, max_count)
            min_cash = self.__min(_result.profit, _result.revenue, _result.cost, min_cash)
            max_cash = self.__max(_result.profit, _result.revenue, _result.cost, max_cash)

        min_count = check_none(min_count)
        max_count = check_none(max_count)
        min_cash = check_none(min_cash)
        max_cash = check_none(max_cash)
        axis = {
            "count" : [min_count, max_count],
            #"cash" : [min_count, max_count],
            "cash" : [min_cash, max_cash],
        }
        return {
            "datas" : result_list,
            "axis" : axis,
        }

    def get_total_static(self):
        items = ['Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'ROI']
        result = []
        total = StatResult()
        for _ts, _result in self._result_list:
            total.add(_result)

        result.append(format_int_comma(total.visits, ","))
        result.append(format_int_comma(total.clicks, ","))
        result.append(format_int_comma(total.conversions, ","))
        result.append('$%s'%(format_float_comma(float('%0.2f'%total.profit),",")))
        result.append('$%s'%(format_float_comma(float('%0.2f'%total.revenue),",")))
        result.append('$%s'%(format_float_comma(float('%0.2f'%total.cost),",")))
        result.append('%0.2f%%'%total.ROI)
        return result, items

class CountryDashboardResult(BaseResult):
    def __init__(self):
        super(CountryDashboardResult, self).__init__()
        self.insert_items(['Country'])
        json_keys = [
            {"key":"country", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('country')
        self.set_sort_default([[2, 'desc']])
        self.add_filter_items('Country', 'contains')
        self.add_dashboard_head(['Country'])
        self.finish_init()

    def load_result(self):
        range_days = self.get_range_days()
        start_day = self.get_start_day()
        for i in xrange(range_days):
            cur_dt = datetime.datetime.fromtimestamp(start_day + i*ONE_DAY_SECONDS)
            datetime_str = cur_dt.strftime('%Y%m%d')
            ts = date_to_ts(cur_dt)
            objs = self.get_static_data(datetime_str, datetime_str, ts)
            if objs:
                for obj in objs:
                    country = str(obj.get("country", ""))
                    if country not in self._result_map:
                        self._result_map[country] = StatResult()
                    self._result_map[country].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        result_list = []
        for country, _result in self._result_map.items():
            items = []
            raw_items = _result.to_raw_items()
            raw_items.insert(0, country)
            for col in filter_col:
                items.append(raw_items[col])
            result_list.append(items)
        return result_list

class OfferDashboardResult(BaseResult):
    def __init__(self):
        super(OfferDashboardResult, self).__init__()
        self.insert_items(['Offer'])
        json_keys = [
            {"key":"oid", "class":Offer, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('offer')
        self.set_sort_default([[0,'asc'],[2, 'desc'],[3, 'desc']])
        self.add_filter_items('Offer', 'contains')
        self.add_dashboard_head(['Offer'])
        self.finish_init()

    def load_result(self):
        range_days = self.get_range_days()
        start_day = self.get_start_day()
        for i in xrange(range_days):
            cur_dt = datetime.datetime.fromtimestamp(start_day + i*ONE_DAY_SECONDS)
            datetime_str = cur_dt.strftime('%Y%m%d')
            ts = date_to_ts(cur_dt)
            objs = self.get_static_data(datetime_str, datetime_str, ts)
            if objs:
                for obj in objs:
                    oid = obj.get("oid", -1)
                    if oid not in self._result_map:
                        self._result_map[oid] = StatResult()
                    self._result_map[oid].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        result_list = []
        names_map = self.get_db_record_names(Offer, uid=self.get_uid())
        for oid, _result in self._result_map.items():
            items = []
            name = names_map.get(oid, "%s"%oid)
            raw_items = _result.to_raw_items()
            raw_items.insert(0, name)
            for col in filter_col:
                items.append(raw_items[col])
            result_list.append(items)
        return result_list


class AdminOfferResult(BaseResult):
    def __init__(self):
        super(AdminOfferResult, self).__init__()
        items = ['User', 'Offer', 'Clicks', 'Convs', 'CR', 'AP', 'Revenue']
        self.set_items(items)
        self.add_items(['oid'])
        json_keys = [
            {"key":"oid", "class" : Offer, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('offer')
        self.set_sort_default([[1,'desc']])
        self.add_filter_items('Offer', 'contains')
        self.add_filter_items('User', 'contains')
        self.finish_init()
        self._offer_map = self._init_offer_class() #oid:direct_url
        self._direct_links = self._init_admin_offer_class()

    def get_all_uids(self):
        res = DBSet.get_db_client().iter_all(User)
        uids = []
        for obj in res:
            uids.append((obj.id, obj.name))
        return uids

    def load_result(self):
        uids = self.get_all_uids()
        for info in uids:
            uid, name = info
            self.set_uid(uid)
            self.set_user_name(name)
            super(AdminOfferResult, self).load_result()

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        user_name = self.get_user_name()
        if objs:
            for obj in objs:
                oid = int(obj.get("oid", -1))
                if oid == -1:
                    continue
                direct_id= self._offer_map.get(oid, 0)
                if direct_id == 0 or direct_id not in self._direct_links:
                    continue
                offer_name = self._direct_links[direct_id]["nick"]
                if user_name not in self._result_map:
                    self._result_map[user_name] = {}
                if direct_id not in self._result_map[user_name]:
                    tmp = StatResult()
                    self._result_map[user_name][direct_id] = (tmp, oid, offer_name, ts)
                self._result_map[user_name][direct_id][0].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        result_list = []
        for user_name, offerObj in self._result_map.items():
            for direct_id, _info in offerObj.items():
                _result, oid, offer_name, ts = _info
                items = []
                items.append(user_name)
                items.append(offer_name)
                items.append(_result.clicks)
                items.append(_result.conversions)
                items.append(_result.CR*0.01)
                items.append(_result.AP)
                items.append(_result.revenue)
                items.append(oid)
                result_list.append(items)
        return result_list

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        for user_name, offerObj in self._result_map.items():
            for direct_id, _info in offerObj.items():
                _result, oid, offer_name, ts = _info
                total.add(_result)
        items = []
        items.append("Total")
        items.append("")
        items.append(total.clicks)
        items.append(total.conversions)
        items.append(total.CR*0.01)
        items.append(total.AP)
        items.append(total.revenue)
        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

class AdminOfferUserResult(BaseResult):
    def __init__(self):
        super(AdminOfferUserResult, self).__init__()
        items = ['User', 'Offer', 'Clicks', 'Convs', 'CR', 'AP', 'Revenue']
        self.set_items(items)
        self.add_items(['oid'])
        json_keys = [
            {"key":"oid", "class" : Offer, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('offer')
        self.set_sort_default([[2,'desc']])
        self.add_filter_items('Offer', 'contains')
        self.add_filter_items('User', 'contains')
        self.finish_init()
        self._offer_map = self._init_offer_class()#oid:direct_url
        self._direct_links = self._init_admin_offer_class()

    def get_all_uids(self):
        res = DBSet.get_db_client().iter_all(User)
        uids = []
        for obj in res:
            uids.append((obj.id, obj.name))
        return uids

    def load_result(self):
        uids = self.get_all_uids()
        for info in uids:
            uid, name = info
            self.set_uid(uid)
            self.set_user_name(name)
            super(AdminOfferUserResult, self).load_result()

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        user_name = self.get_user_name()
        if objs:
            for obj in objs:
                oid = int(obj.get("oid", -1))
                if oid == -1:
                    continue
                direct_id= self._offer_map.get(oid, 0)
                if direct_id == 0 or direct_id not in self._direct_links:
                    continue
                offer_name = self._direct_links[direct_id]["nick"]
                if not self.is_valid_rules({"d_oid_name":offer_name}):
                    continue
                if user_name not in self._result_map:
                    tmp = StatResult()
                    self._result_map[user_name] = (tmp, oid, offer_name, direct_id, ts)
                self._result_map[user_name][0].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        result_list = []
        for _key, _info in self._result_map.items():
            _result, oid, offer_name, direct_id, ts = _info
            items = []
            items.append(_key)
            items.append(offer_name)
            items.append(_result.clicks)
            items.append(_result.conversions)
            items.append(_result.CR*0.01)
            items.append(_result.AP)
            items.append(_result.revenue)
            items.append(oid)
            result_list.append(items)
        return result_list

class UserOfferResult(BaseResult):
    def __init__(self):
        super(UserOfferResult, self).__init__()
        items = ['Offer', 'Clicks', 'Convs', 'CR', 'AP', 'Revenue']
        self.set_items(items)
        self.add_items(['oid'])
        json_keys = [
            {"key":"oid", "class" : Offer, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('offer')
        self.set_sort_default([[1,'desc']])
        self.add_filter_items('Offer', 'contains')
        self.finish_init()
        self._offer_map = self._init_offer_class() #oid:direct_url
        self._direct_links = self._init_admin_offer_class()

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for obj in objs:
                oid = int(obj.get("oid", -1))
                if oid == -1:
                    continue
                direct_id = self._offer_map.get(oid, 0)
                if direct_id == 0 or direct_id not in self._direct_links:
                    continue
                offer_name = self._direct_links[direct_id]["nick"]
                if direct_id not in self._result_map:
                    tmp = StatResult()
                    self._result_map[direct_id] = (tmp, oid, offer_name, ts)
                self._result_map[direct_id][0].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        result_list = []
        for direct_id, _info in self._result_map.items():
            _result, oid, offer_name, ts = _info
            items = []
            items.append(offer_name)
            items.append(_result.clicks)
            items.append(_result.conversions)
            items.append(_result.CR*0.01)
            items.append(_result.AP)
            items.append(_result.revenue)
            items.append(oid)
            result_list.append(items)
        return result_list

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        for direct_id, _info in self._result_map.items():
            _result, oid, offer_name, ts = _info
            total.add(_result)
        items = []
        items.append("Total")
        items.append(total.clicks)
        items.append(total.conversions)
        items.append(total.CR*0.01)
        items.append(total.AP)
        items.append(total.revenue)
        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

class UserDirectPBResult(BaseResult):
    def __init__(self):
        super(UserDirectPBResult, self).__init__()
        items = ['Offer', 'Clicks', 'Convs', 'CR', 'AP', 'Revenue']
        self.set_items(items)
        self.add_items(['oid'])
        json_keys = [
            {"key":"oid", "class" : Offer, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('offer')
        self.set_sort_default([[1,'desc']])
        self.add_filter_items('Offer', 'contains')
        self.finish_init()
        self._offer_map = self._init_offer_class() #oid:direct_url
        self._direct_links = self._init_admin_offer_class()
        self.set_prefix_filename("pb_")

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for obj in objs:
                oid = int(obj.get("oid", -1))
                if oid == -1:
                    continue
                direct_id = self._offer_map.get(oid, 0)
                if direct_id == 0 or direct_id not in self._direct_links:
                    continue
                offer_name = self._direct_links[direct_id]["nick"]
                if direct_id not in self._result_map:
                    tmp = StatResult()
                    self._result_map[direct_id] = (tmp, oid, offer_name, ts)
                self._result_map[direct_id][0].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        result_list = []
        for direct_id, _info in self._result_map.items():
            _result, oid, offer_name, ts = _info
            items = []
            items.append(offer_name)
            items.append(_result.clicks)
            items.append(_result.conversions)
            items.append(_result.CR*0.01)
            items.append(_result.AP)
            items.append(_result.revenue)
            items.append(oid)
            result_list.append(items)
        return result_list

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        for direct_id, _info in self._result_map.items():
            _result, oid, offer_name, ts = _info
            total.add(_result)
        items = []
        items.append("Total")
        items.append(total.clicks)
        items.append(total.conversions)
        items.append(total.CR*0.01)
        items.append(total.AP)
        items.append(total.revenue)
        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

class AdminDirectPBResult(BaseResult):
    def __init__(self):
        super(AdminDirectPBResult, self).__init__()
        items = ['User', 'Offer', 'Clicks', 'Convs', 'CR', 'AP', 'Revenue']
        self.set_items(items)
        self.add_items(['oid'])
        json_keys = [
            {"key":"oid", "class" : Offer, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('offer')
        self.set_sort_default([[2,'desc']])
        self.add_filter_items('Offer', 'contains')
        self.add_filter_items('User', 'contains')
        self.finish_init()
        self._offer_map = self._init_offer_class() #oid:direct_url
        self._direct_links = self._init_admin_offer_class()
        self.set_prefix_filename("pb_")

    def get_all_uids(self):
        res = DBSet.get_db_client().iter_all(User)
        uids = []
        for obj in res:
            uids.append((obj.id, obj.name))
        return uids

    def load_result(self):
        uids = self.get_all_uids()
        for info in uids:
            uid, name = info
            self.set_uid(uid)
            self.set_user_name(name)
            super(AdminDirectPBResult, self).load_result()

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        user_name = self.get_user_name()
        if objs:
            for obj in objs:
                oid = int(obj.get("oid", -1))
                if oid == -1:
                    continue
                direct_id = self._offer_map.get(oid, 0)
                if direct_id == 0 or direct_id not in self._direct_links:
                    continue
                offer_name = self._direct_links[direct_id]["nick"]
                if user_name not in self._result_map:
                    self._result_map[user_name] = {}
                if direct_id not in self._result_map[user_name]:
                    tmp = StatResult()
                    self._result_map[user_name][direct_id] = (tmp, oid, offer_name, ts)
                self._result_map[user_name][direct_id][0].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        result_list = []
        for user_name, offerObj in self._result_map.items():
            for direct_id, _info in offerObj.items():
                _result, oid, offer_name, ts = _info
                items = []
                items.append(user_name)
                items.append(offer_name)
                items.append(_result.clicks)
                items.append(_result.conversions)
                items.append(_result.CR*0.01)
                items.append(_result.AP)
                items.append(_result.revenue)
                items.append(oid)
                result_list.append(items)
        return result_list

    def get_bottom_static(self):
        result_list = []
        total = StatResult()
        for user_name, offerObj in self._result_map.items():
            for direct_id,  _info in offerObj.items():
                _result, oid, offer_name, ts = _info
                total.add(_result)
        items = []
        items.append("Total")
        items.append("")
        items.append(total.clicks)
        items.append(total.conversions)
        items.append(total.CR*0.01)
        items.append(total.AP)
        items.append(total.revenue)
        items.append(-1)
        tmp = {}
        for i in xrange(len(items)):
            tmp[self._items[i]] = items[i]
        result_list.append(tmp)
        return result_list

class EventCampaignReportResult(BaseResult):
    def __init__(self):
        super(EventCampaignReportResult, self).__init__()
        items = ['Date', 'Campaign', 'Type', 'Visit', 'Description']
        self.set_items(items)
        self.add_items(['cpid'])
        json_keys = [
            {"key":"cpid", "class" : Campaign, "is_rule":False},
        ]

        self.set_tag('campaign')
        self.set_sort_default([[0,'desc'],[1,'asc']])
        self.add_filter_items('Campaign', 'contains')
        self.add_filter_items('Date', 'contains')
        self.add_filter_items('Type', 'contains')
        self.finish_init()
        self.set_prefix_filename("event_")

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for cpid, info in objs.items():
                if cpid not in self._result_map:
                    self._result_map[cpid] = {}
                for key, _data in info.items():
                    if key not in self._result_map[cpid]:
                        self._result_map[cpid][key] = {}
                    for f, obj in _data.items():
                        if len(obj) == 4:
                            campaign_name, fomular, ts, visits = obj
                        else:
                            campaign_name, fomular, ts = obj
                            visits = 0
                        items = []
                        time_str = ts_to_str_min(ts)
                        items.append(time_str)
                        items.append(campaign_name)
                        items.append(key)
                        items.append(visits)
                        items.append(fomular)
                        items.append(cpid)
                        self._result_list.append(items)
                        self._result_map[cpid][key][f] = (campaign_name, fomular, ts, visits)

    def get_raw_data(self, filter_col=None):
        return self._result_list

class EventOfferReportResult(BaseResult):
    def __init__(self):
        super(EventOfferReportResult, self).__init__()
        items = ['Date', 'Offer', 'Type', 'Conv', 'Description']
        self.set_items(items)
        self.add_items(['oid'])
        json_keys = [
            {"key":"oid", "class" : Offer, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('offer')
        self.set_sort_default([[0,'desc'],[1,'asc']])
        self.add_filter_items('Offer', 'contains')
        self.add_filter_items('Date', 'contains')
        self.add_filter_items('Type', 'contains')
        self.finish_init()
        self.set_prefix_filename("event_")

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for oid, info in objs.items():
                if oid not in self._result_map:
                    self._result_map[oid] = {}
                for key, _data  in info.items():
                    if key not in self._result_map[oid]:
                        self._result_map[oid][key] = {}
                    for f, obj in _data.items():
                        self._result_map[oid][key][f] = obj

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        for oid, keyObj in self._result_map.items():
            for key, info in keyObj.items():
                for t, obj in info.items():
                    conv, visits, description, ts = obj
                    items = []
                    time_str = ts_to_str_min(ts)
                    items.append(time_str)
                    oid_name = names_map["oid"].get(int(oid), str(oid))
                    items.append(oid_name)
                    items.append(key)
                    items.append(conv)
                    #items.append(visits)
                    items.append(description)
                    items.append(oid)
                    self._result_list.append(items)

        return self._result_list

class EventValveOfferReportResult(BaseResult):
    def __init__(self):
        super(EventValveOfferReportResult, self).__init__()
        items = ['Date', 'Offer', 'Type', 'Conv', 'Description']
        self.set_items(items)
        self.add_items(['oid'])
        json_keys = [
            {"key":"oid", "class" : Offer, "is_rule":False},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('valve_offer')
        self.set_sort_default([[0,'desc'],[1,'asc']])
        self.add_filter_items('Offer', 'contains')
        self.add_filter_items('Date', 'contains')
        self.add_filter_items('Type', 'contains')
        self.finish_init()
        self.set_prefix_filename("event_")

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for oid, info in objs.items():
                if oid not in self._result_map:
                    self._result_map[oid] = {}
                for key, _data  in info.items():
                    if key not in self._result_map[oid]:
                        self._result_map[oid][key] = {}
                    for f, obj in _data.items():
                        self._result_map[oid][key][f] = obj

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        for oid, keyObj in self._result_map.items():
            for key, info in keyObj.items():
                for t, obj in info.items():
                    conv, visits, description, ts = obj
                    items = []
                    time_str = ts_to_str_min(ts)
                    items.append(time_str)
                    oid_name = names_map["oid"].get(int(oid), str(oid))
                    items.append(oid_name)
                    items.append(key)
                    items.append(conv)
                    #items.append(visits)
                    items.append(description)
                    items.append(oid)
                    self._result_list.append(items)

        return self._result_list

class PBOfferResult(BaseResult):
    def __init__(self):
        super(PBOfferResult, self).__init__()
        self.insert_items(['Campaign', 'Offer'])
        self.add_items(['cpid', 'oid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"oid", "class":Offer, "is_rule":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('offer')
        self.set_sort_default([[0,'asc'],[2, 'desc'],[3, 'desc']])
        self.add_filter_items('Offer', 'contains')
        self.add_dashboard_head(['Offer'])
        self.set_prefix_filename("pb_")
        self.finish_init()

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        result_list = []
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()
            items[6] = 0.0
            for i in range(len(key_list)-1, -1,-1):
                k = key_list[i]
                jk_k = self._json_keys[i].get("key", None)
                if jk_k and jk_k in names_map:
                    name = names_map[jk_k].get(k, "%s"%k)
                    items.insert(0, name)
                else:
                    items.insert(0, k)
            if self._is_show_date:
                dt = ts_to_date(ts)
                datetime_str = dt.strftime('%Y%m%d')
                items = _result.to_raw_items()
                items.insert(0, datetime_str[4:])

            for i in xrange(len(key_list)):
                if self._json_keys[i].get("add_ignore", None):
                    continue
                k = key_list[i]
                items.append(k)
            if filter_col:
                filter_items = []
                for col in filter_col:
                    filter_items.append(items[col])
                items = filter_items
            result_list.append(items)
        return result_list

class Tok1Result(BaseResult):
    def __init__(self):
        super(Tok1Result, self).__init__()
        self.insert_items(['Campaign', 'Tok1'])
        self.add_items(['cpid', 'tok1'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"tok1", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('tok1')
        self.set_sort_default([[0,'asc'],[2, 'desc'],[3, 'desc']])
        self.add_filter_items('Tok1', 'contains')
        self.finish_init()

class Tok2Result(BaseResult):
    def __init__(self):
        super(Tok2Result, self).__init__()
        self.insert_items(['Campaign', 'Tok2'])
        self.add_items(['cpid', 'tok2'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"tok2", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('tok2')
        self.set_sort_default([[0,'asc'],[2, 'desc'],[3, 'desc']])
        self.add_filter_items('Tok2', 'contains')
        self.finish_init()

class Tok3Result(BaseResult):
    def __init__(self):
        super(Tok3Result, self).__init__()
        self.insert_items(['Campaign', 'Tok3'])
        self.add_items(['cpid', 'tok3'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"tok3", "class":None, "is_rule":False, "add_ignore":True},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('tok3')
        self.set_sort_default([[0,'asc'],[2, 'desc'],[3, 'desc']])
        self.add_filter_items('Tok3', 'contains')
        self.finish_init()


class MobvistaOffer(BaseResult):
    def __init__(self):
        super(MobvistaOffer, self).__init__()
        items = ["state", "campaign_id", "title", "payout", "trace_app_id", "allow_country", "allow_device","android_version","link_type","startrate","cap","category","begintime","endtime","appsize","preview_url","icon_url","impression_url","trackurl","appdesc"]
        self.set_items(items)
        self.set_files_path(settings.mobvista_json_dir)
        self.set_tag('campaigns')
        self.set_sort_default([[1,'asc']])
        self.add_filter_items('campaign_id', 'contains')
        self.add_filter_items('allow_country', 'contains')
        self.add_filter_items('allow_device', 'contains')
        self.add_filter_items('cap', 'lt')
        self.add_filter_items('state', 'contains')
        self.add_filter_items('title', 'contains')
        self._load_file_name = ""
        self.finish_init()

    def get_normal_items(self):
        items = ["state", "campaign_id",  "title", "begintime", "endtime", "preview_url", "icon_url", "payout", "cap", "allow_country", "allow_device", "impression_url", "trackurl"]
        return items

    def get_detail_items(self):
        items = ["trace_app_id", "link_type", "android_version", "startrate", "appsize", "appdesc"]
        return items

    def set_load_filename(self, filename):
        self._load_file_name = filename

    def load_result(self):
        if self._load_file_name == "" :
            return
        self._load_mv_files(self._load_file_name)

    def _load_mv_files(self, filename):
        full_path = osp.join(self.get_files_path(), str(self.get_uid()), filename)
        key = "mvoffer_inapp"
        obj = self.get_cache(key)
        if obj is None:
            obj = self.get_static_data_from_file(full_path)
        if obj is None:
            return
        data = obj.get(self.get_tag(), None)
        if data is None:
            return
        self._result_map = {}
        filter_oid = str(self._rules.get("oid", "-1"))
        for campaign_id, info in data.iteritems():
            if filter_oid != "-1":
                if info.get('campaign_id', "") == filter_oid:
                    self._result_map[campaign_id] = info
                    break
            else:
                self._result_map[campaign_id] = info

    def _cal_state(self, cur_ts, start_ts, end_ts):
        if cur_ts < start_ts:
            return "Unopened"
        elif cur_ts > end_ts:
            return "Expire"
        else:
            if (end_ts - cur_ts) <= ONE_DAY_SECONDS:
                return "Ready to Stop(1 day)"
            return "Running"

    def get_raw_data(self, filter_col=None):
        ignore_items = ["state"]
        data = []
        cur_ts = int(time.time())
        for campaign_id, info in self._result_map.iteritems():
            items = []
            tags = self.get_items()
            start_ts = 0
            end_ts = 0
            for tag in tags:
                if tag in ignore_items:
                    continue
                v = info.get(tag, "")
                if tag == "begintime" or tag == "endtime":
                    if tag == "begintime":
                        start_ts = int(v)
                    elif tag == "endtime":
                        end_ts = int(v)
                    dt = ts_to_date(int(v))
                    v = dt.strftime('%Y-%m-%d %H:%M:%S')
                if tag == "cap":
                    v = int(v)
                items.append(v)
            state = self._cal_state(cur_ts, start_ts, end_ts)
            items.insert(0, state)
            data.append(items)
        return data

    def get_kendo_data(self):
        ret = super(MobvistaOffer, self).get_kendo_data()
        ret["normal_items"] = self.get_normal_items()
        ret["detail_items"] = self.get_detail_items()
        return ret


class MobvistaDiffOffer(MobvistaOffer):
    def __init__(self):
        super(MobvistaDiffOffer, self).__init__()
        items = ["state", "time", "campaign_id", "payout", "title"]
        #items = ["state", "time", "campaign_id", "title", "payout", "trace_app_id", "allow_country", "allow_device","android_version","link_type","startrate","cap","category","begintime","endtime","appsize","preview_url","icon_url","impression_url","trackurl","appdesc"]
        self.set_items(items)
        self.set_files_path(settings.mobvista_json_dir)
        self.set_tag('campaigns')
        self.set_sort_default([[1,'desc']])
        self.add_filter_items('campaign_id', 'contains')
        #self.add_filter_items('allow_country', 'contains')
        #self.add_filter_items('allow_device', 'contains')
        #self.add_filter_items('cap', 'lt')
        self.add_filter_items('state', 'contains')
        self.add_filter_items('title', 'contains')
        self.add_filter_items('time', 'contains')
        self._load_file_name = ""
        self.finish_init()

    def _load_mv_files(self, filename):
        cache_key = "mvoffer_modify"
        obj = self.get_cache(cache_key)
        uid = 1
        if not obj:
            full_path = osp.join(self.get_files_path(), str(uid), filename)
            obj = self.get_static_data_from_file(full_path)
        if obj is None:
            return
        self._result_map = obj

    def get_normal_items(self):
        items = ["state", "time", "campaign_id",  "title", "begintime", "endtime", "preview_url", "icon_url", "payout", "cap", "allow_country", "allow_device", "impression_url", "trackurl"]
        return items

    def get_detail_items(self):
        items = ["trace_app_id", "link_type", "android_version", "startrate", "appsize", "appdesc"]
        return items

class IronSourceOffer(BaseResult):
    def __init__(self):
        super(IronSourceOffer, self).__init__()
        items = ["campaign_id", "internal_campaign_id", "offer_id", "internal_offer_id", "packageName", "title", "bid", "rating", "platform", "downloads", "creatives", "geoTargeting", "category", "packageSize", "deviceTypes", "connectionType", "impressionURL", "clickURL", "minOSVersion", "description"]
        self.set_items(items)
        self.set_files_path(settings.mobvista_json_dir)
        self.set_tag('ads')
        self.set_sort_default([[0,'asc']])

        self.add_filter_items('offer_id', 'contains')
        self.add_filter_items('campaign_id', 'contains')
        self.add_filter_items('packageName', 'contains')
        self.add_filter_items('title', 'contains')
        self.add_filter_items('platform', 'contains')
        self.add_filter_items('geoTargeting', 'contains')
        self.add_filter_items('deviceTypes', 'contains')
        self.add_filter_items('connectionType', 'contains')
        self.add_filter_items('bid', 'lt')
        self.add_filter_items('rating', 'lt')
        self._load_file_name = ""
        self.finish_init()

    def get_normal_items(self):
        items = ["campaign_id", "internal_campaign_id", "offer_id", "internal_offer_id", "packageName", "bid", "rating", "impressionURL", "clickURL", "platform", "title", "geoTargeting", "deviceTypes", "connectionTypes"]
        return items

    def get_detail_items(self):
        items = ["description", "downloads", "category", "packageSize", "minOSVersion"]
        return items

    def set_load_filename(self, filename):
        self._load_file_name = filename

    def load_result(self):
        if self._load_file_name == "" :
            return
        self._load_is_files(self._load_file_name)

    def _load_is_files(self, filename):
        full_path = osp.join(self.get_files_path(), str(self.get_uid()), filename)
        key = "iron_source"
        obj = self.get_cache(key)
        if obj is None:
            obj = self.get_static_data_from_file(full_path)
        if obj is None:
            return
        data = obj.get(self.get_tag(), None)
        if data is None:
            return
        self._result_map = {}
        array_item = ["geoTargeting", "deviceTypes"]
        int2str_item = ["campaign_id", "internal_campaign_id", "offer_id", "internal_offer_id"]
        filter_oid = str(self._rules.get("oid", -1))
        for offerInfo in data:
            tmp = {}
            for item in self.get_items():
                v = offerInfo.get(item, "")
                if item in array_item:
                    v = ",".join(v)
                if item in int2str_item:
                    v = str(v)
                tmp[item] = v

            if filter_oid != "-1":
                if tmp.get("campaign_id", "") == filter_oid:
                    self._result_map[filter_oid] = tmp
                    break
            else:
                self._result_map[tmp["campaign_id"]] = tmp

    def get_raw_data(self, filter_col=None):
        data = []
        tags = self.get_items()
        for offer_id, info in self._result_map.iteritems():
            items = []
            for tag in tags:
                v = info.get(tag, "")
                items.append(v)
            data.append(items)
        return data

    def get_kendo_data(self):
        ret = super(IronSourceOffer, self).get_kendo_data()
        ret["normal_items"] = self.get_normal_items()
        ret["detail_items"] = self.get_detail_items()
        return ret

class IronSourceDiffOffer(IronSourceOffer):
    def __init__(self):
        super(IronSourceDiffOffer, self).__init__()
        items = ["time", "campaign_id", "offer_id", "bid", "title"]
        self.set_items(items)
        self.set_files_path(settings.mobvista_json_dir)
        self.set_tag('campaigns')
        self.set_sort_default([[1,'desc']])
        self.add_filter_items('campaign_id', 'contains')
        self.add_filter_items('offer_id', 'contains')
        self.add_filter_items('time', 'contains')
        self.add_filter_items('bid', 'lt')
        self._load_file_name = ""
        self.finish_init()

    def _load_is_files(self, filename):
        cache_key = "isoffer_modify"
        obj = self.get_cache(cache_key)
        uid = 1
        if not obj:
            full_path = osp.join(self.get_files_path(), str(uid), filename)
            obj = self.get_static_data_from_file(full_path)
        if obj is None:
            return
        self._result_map = obj

    def get_normal_items(self):
        items = []
        return items

    def get_detail_items(self):
        items = []
        return items

class ZeroPark(BaseResult):
    def __init__(self):
        super(ZeroPark, self).__init__()
        self.set_files_path(settings.zeropark_json_dir)
        self.set_prefix_filename("zeropark_")
        self.cache = None
        self.cache_handler = None
        self.cache_tag = None
        self._add_template_format("profit", "c2")
        self._add_template_format("m_revenue", "c2")
        self._add_template_format("m_visits", "n0")
        self._add_template_format("m_clicks", "n0")
        self._add_template_format("m_convs", "n0")
        self._add_template_format("redirects", "n0")
        self._add_template_format("m_cost", "c2")
        self._add_template_format("spent", "c2")
        self._add_template_format("topBid", "c6")
        self._add_template_format("bid", "c3")
        self._add_template_format("averageBid", "c3")
        self._add_templaet_format("availableVisits", "n0")

    def set_cache_handler(self, func):
        self.cache_handler = func

    def set_cache_tag(self, tag):
        self.cache_tag = tag

    def set_tag(self, tag):
        self.tag = tag

    def get_file_full_name(self, file_name):
        return  "%s%s.json" % (self.get_prefix_filename(), file_name)

    def _set_data_cache(self, obj, file_name, ts):
        #set modify time cache
        file_path = self._do_get_file_path(file_name)
        last_time = self.get_file_modify_time(file_path)
        if last_time != -1:
            self.set_cache(self.get_mss_cachetime_key(file_name), last_time, ts)
        s_key = self.get_mss_db_key(ts, 'common')
        self.set_cache(s_key, json.dumps(obj), ts)

    def load_result(self):
        range_days = self.get_range_days()
        start_day = self.get_start_day()
        self.cache = {}
        self._result_map = []
        for i in xrange(range_days):
            cur_dt = datetime.datetime.fromtimestamp(start_day+ i*ONE_DAY_SECONDS)
            datetime_str = cur_dt.strftime('%Y%m%d')
            ts = str_day_to_ts(datetime_str)
            file_path = self._do_get_file_path(datetime_str)
            key = self.get_mss_db_key(ts, 'common')
            data = self.get_cache(key)
            if not data or self.check_file_is_modify(file_path, datetime_str):
                data = self.get_data_from_file(file_path)
                self._set_data_cache(data, datetime_str, ts)
            self._result_map.append((datetime_str, data))
            cache_data = data.get(self.cache_tag, None) if data and self.cache_tag else None
            if self.cache_handler and cache_data:
                cache_data = self.cache_handler(cache_data)
                self.cache.update(cache_data)
        self._result_map.sort(key=lambda a:a[0])

    def get_mss_db_key(self, ts, tag=None):
        tag = tag or self.get_tag()
        data_type = 0
        return "zeropark_%s_%s_%s_%s" % (self.get_uid(), data_type, tag, ts)

    def get_join_mss_cachetime_key(self, file_name, prefix=""):
        is_full_day = self.get_full_day()
        data_type = 0 if is_full_day else 1
        return "%s_%s_%s_%s" % (prefix, self.get_uid(), data_type, file_name)

    def check_join_file_is_modify(self, path, file_name, prefix=""):
        last_time = self.get_file_modify_time(path)
        cache_time = self.get_cache(self.get_join_mss_cachetime_key(file_name, prefix=prefix))
        if cache_time is None:
            cache_time = -1
        return cache_time != last_time

    def set_join_data_cache(self, obj, file_name, ts, prefix=""):
        #set modify time cache
        file_dir = osp.join(settings.json_dir, str(self.get_uid()))
        file_path = osp.join(file_dir, "%s.tar.gz"%file_name)
        last_time = self.get_file_modify_time(file_path)
        if last_time != -1:
            self.set_cache(self.get_join_mss_cachetime_key(file_name, prefix=prefix), last_time, ts)
        for tag in ALL_TAGS:
            s = obj.get(tag, None)
            if s is None:
                continue
            s_key = self.get_join_mss_db_key(ts, tag, prefix=prefix)
            self.set_cache(s_key, json.dumps(s), ts)

    def get_data_from_file(self, file_path):
        data = None
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                s = "".join(lines)
                s = decode_from_utf8(s)
                data = json.loads(s)
        except Exception, ex:
            print ex
        return data

        #table_tags[tag] = ins.get_items()

    def get_massival_report(self, date_str, tag, tar_prefix="", ssdb_key_prefix=""):
        k = str_day_to_ts(date_str)
        key = self.get_join_mss_db_key(k, tag, prefix=ssdb_key_prefix)
        data = self.get_cache(key)
        file_name =  "%s.tar.gz"%date_str
        file_dir = osp.join(settings.json_dir, str(self.get_uid()))
        file_path = osp.join(file_dir, file_name)

        if data and not self.check_join_file_is_modify(file_path, date_str, prefix=ssdb_key_prefix):
            return data
        obj =  self.read_massival_report(file_path, date_str, tar_prefix)
        data = obj.get(tag, [])
        if data:
            self.set_join_data_cache(obj, date_str, k, prefix=ssdb_key_prefix)
        return data

    def read_massival_report(self, file_path, date_str, tar_prefix):
        data = {}
        try:
            tarObj = tarfile.open(file_path, "r:*")
            obj = tarObj.getmember("%s%s.json"%(tar_prefix, date_str))
            f = tarObj.extractfile(obj)
            lines = f.readlines()
            s = "".join(lines)
            s = decode_from_utf8(s)
            ret_data = json.loads(s)
            return ret_data
        except Exception, ex:
            print ex
        return data

    def get_join_mss_db_key(self, ts, tag=None, prefix=""):
        tag = tag or self.get_tag()
        is_full_day = self.get_full_day()
        data_type = 0 if is_full_day else 1
        return "%s_%s_%s_%s_%s" % (prefix, self.get_uid(), data_type, tag, ts)

    def finish_init(self):
        formats = {
            "profit" : {"reg":"$"},
            "ROI" : {"reg":"%"}
            }
        self.add_column_format(formats)

    def is_crypt_user(self):
        user = DBSet.get_db_client().select_one(User, id=self._my_uid)
        return check_permission(PERMISSION_REPORT, user.permission, PERMISSION_REPORT_ZERO_ENCRYPT)


def flat_dict(d, name = ""):
    r = {}
    for k, v in d.items():
        kk = k if not name else "%s_%s"%(name, k)
        if type(v) == dict:
            ret = flat_dict(v, kk)
            r.update(ret)
        elif type(v) == list:
            r[kk] = ",".join([str(e) for e in v])
        else:
            r[kk] = v
    return r

def calc(data, flat_date=False):
    ret = {}
    ori_data_str = ""
    replace_keys = ['target', 'name', 'geo', 'url',  'trafficSourceType', 'type', 'position', 'state_actions', 'dailyBudget_type', 'totalBudget_type', 'state_state']
    sum_keys = ['spent', 'payout', 'redirects', 'totalBudget_amount', 'conversions', 'm_clicks', 'm_visits', 'm_revenue', 'm_convs', 'm_cost', 'profit']
    max_keys = ['topBid']
    avg_keys = ['dailyBudget_amount']
    for date_str, datas in data:
        for d in datas:
            rec = ret.get(d['id'])
            if not rec:
                ret[d['id']] = d
                continue
            for k, v in d.items():
                if k in replace_keys:
                    rec[k] = v
                elif k in sum_keys:
                    val = rec.get(k)
                    rec[k] = v if not val else v + val
                elif k in max_keys:
                    if k not in rec or rec[k] < d[k]:
                        rec[k] = d[k]
                elif k in avg_keys:
                    if k not in rec:
                        rec[k] = []
                    if type(rec[k]) != list:
                        rec[k] = [rec[k]]
                    rec[k].append(v)
    for _k, rec in ret.iteritems():
        calc_higher_order_args(rec)
        if 'averageBid' in rec:
            spent = rec.get('spent', 0.0)
            visit = rec.get('redirects', 0)
            rec['averageBid'] = spent/visit
        else:
            for k in avg_keys :
                if k in rec:
                    rec[k] = sum(rec[k])/len(rec[k])
    return ret.values()

def calc_higher_order_args(rec):
    if 'redirects' in rec and rec['redirects'] != 0:
        rec['CTR'] = rec.get('m_clicks', 0) * 1.0 /rec['redirects']
        rec['CPM'] = rec.get('spent', 0.0)/rec['redirects'] * 1000
        rec['EPM'] = rec.get('m_revenue', 0)/rec['redirects'] * 1000
    else:
        rec['CTR'] = 0
        rec['CPM'] = 0
        rec['EPM'] = 0
    if 'spent' in rec and rec['spent'] != 0:
        rec['ROI'] = (rec.get('m_revenue', 0.0) * 1.0 - rec['spent'])/rec['spent']
    else:
        rec['ROI'] = 0.0


class ZeroParkCamp(ZeroPark):
    def __init__(self):
        super(ZeroParkCamp, self).__init__()
        self.set_tag("campaign")
        self.set_sort_default([[0, 'desc']])
        keys = [u'name', u'id', u'm_name', u'm_cpid', u'zero_id', u'redirects', u'm_visits', u'm_clicks', u'm_convs', u'profit', u'm_revenue', u'spent', u'm_cost', u'CPM', u'CTR', u'ROI', u'EPM', u'topBid', u'url', u'geo', u'bid', u'averageBid', u'trafficSourceType', u'type', u'position', u'state_actions', u'state_state', u'dailyBudget_type', u'dailyBudget_amount', u'totalBudget_type', u'totalBudget_amount']
        self.set_items(keys)
        self._ignore_items = [1, 3, 4]
        self.add_filter_items('name', 'contains')
        self.add_filter_items('url', 'contains')
        self.set_sort_default([[4,'desc']])
        self.finish_init()

    def join_camp_report(self, cpid_urls, data):
        ret = {}
        for date_str, api_reports in data:
            tmp_reports = self.get_massival_report(date_str, 'campaign')
            massival_report = {}
            for r in tmp_reports:
                massival_report[r['cpid']] = r
            for r in api_reports:
                rpt = {}
                for cpid, url, name in cpid_urls:
                    if url in r['url']:
                        rpt = massival_report.get(cpid, {})
                        r['m_name'] = name
                        break
                r['m_revenue'] = rpt.get('revenue', 0.0)
                r['m_clicks'] = rpt.get('clicks', 0)
                r['m_visits'] = rpt.get('visits', 0)
                r['m_convs'] = rpt.get('conversions', 0)
                r['m_cost'] = rpt.get('cost', 0)
                r['m_cpid'] = rpt.get('cpid', 0)
                r['profit'] = r['m_revenue'] - r['spent']
        return data

    def get_kendo_data(self):
        uid = self.get_uid()
        camps = DBSet.get_db_client().iter_all(Campaign, uid=uid)
        cpid_url = []
        for camp in camps:
            cpid_url.append((camp.id, camp.uri, camp.name))

        data = []
        keys = set()
        d = [(date_str, [dd for dd in d[self.tag] if dd['redirects']]) for date_str, d in self._result_map if d]
        d = self.join_camp_report(cpid_url, d)
        api_args = {"type":"camp", "action":["pause", "resume"]}

        data = calc(d)
        result = {}
        result["head"] = self._items
        result["data"] = data
        result["hidden"] = self._ignore_items
        result["filter"] = self._filter_items
        result["format"] = self.get_template_format()
        result["default_sort"] =  self.get_default_sort()
        result["bottom_static"] = self.get_bottom_static()
        result["tips"] = self.get_help_tips(),
        return result

class ZeroParkCampDate(ZeroPark):
    def __init__(self):
        super(ZeroParkCampDate, self).__init__()
        self.set_tag("campaign")
        self.set_sort_default([[0, 'desc']])
        keys = [u'name', u'id', u'zero_id', u'date', u'redirects', u'm_visits', u'm_clicks', u'm_convs', u'profit', u'm_revenue', u'spent', u'm_cost', u'CPM', u'CTR', u'ROI', u'EPM' , u'topBid', u'url', u'geo', u'bid', u'averageBid', u'trafficSourceType', u'type', u'position', u'state_actions', u'state_state', u'dailyBudget_type', u'dailyBudget_amount', u'totalBudget_type', u'totalBudget_amount']
        self.set_items(keys)
        self._ignore_items = [1, 2]
        self.add_filter_items('name', 'contains')
        self.add_filter_items('url', 'contains')
        self.finish_init()

    def join_camp_report(self, cpid, data):
        d = []
        for date_str, api_report in data:
            tmp_reports = self.get_massival_report(date_str, 'campaign')
            massival_report = {}
            for r in tmp_reports:
                massival_report[r['cpid']] = r
            rpt = massival_report.get(cpid, {})
            api_report['date'] = date_str
            api_report['m_revenue'] = rpt.get('revenue', 0.0)
            api_report['m_clicks'] = rpt.get('clicks', 0)
            api_report['m_visits'] = rpt.get('visits', 0)
            api_report['m_convs'] = rpt.get('conversions', 0)
            api_report['m_cost'] = rpt.get('cost', 0)
            api_report['profit'] = api_report['m_revenue'] - api_report['spent']
            calc_higher_order_args(api_report)
            d.append(api_report)
        return d

    def get_kendo_data(self):
        uid = self.get_uid()
        camps = DBSet.get_db_client().iter_all(Campaign, uid=uid)
        cpid_url = []
        zero_cpid = self._rules['cpid']
        url_args = self.get_url_args()
        cpname = url_args['cpname']

        data = []
        keys = set()
        cp_url = ""
        for date_str, d in self._result_map:
            if not d:
                continue
            tmp = {}

            for dd in d['campaign']:
                if dd['id'] == zero_cpid:
                    tmp = dd
                    cp_url = dd['url']
                    break
            if not tmp:
                tmp['name'] = cpname
                tmp['redirects'] = 0
                tmp['spent'] = 0
            data.append((date_str, tmp))

        report_cpid = 0
        for camp in camps:
            if camp.uri in cp_url:
                report_cpid = camp.id

        data = self.join_camp_report(report_cpid, data)

        result = {}
        result["head"] = self._items
        result["data"] = data
        result["hidden"] = self._ignore_items
        result["filter"] = self._filter_items
        result["format"] = self.get_template_format()
        result["default_sort"] =  self.get_default_sort()
        result["bottom_static"] = self.get_bottom_static()
        result["tips"] = self.get_help_tips()
        return result

class ZeroParkTarget(ZeroPark):
    def __init__(self):
        super(ZeroParkTarget, self).__init__()
        self.set_cache_tag("campaign")
        self.set_tag("target")
        self.set_cache_handler(self.gen_camp_id2name_map)
        self.set_sort_default([[0, 'desc']])
        keys = [u'target', u'redirects', u'm_visits', u'm_clicks', u'm_convs', u'profit', u'm_revenue', u'spent', u'm_cost', u'CPM', u'CTR', u'ROI', u'EPM', u'averageBid', u"availableVisits", u'topBid', u'bid_autoBid', u'trafficSourceType', u'position', u'state_actions', u'state_state']
        self.set_items(keys)
        self.add_filter_items('target', "contains")
        self.set_sort_default([[1,'desc']])
        self.finish_init()

    def gen_camp_id2name_map(self, data):
        d = {}
        for camp in data:
            name = camp['name']
            cpid = camp['id']
            d[cpid] = name
        return d

    def init_warn_result(self, data):
        data = [d for d in data if d['m_visits'] > 1000 and d['m_convs'] == 0]

        result = {
            "tag" : table_tag_config[ZEROPARK_WARN_TARGET_TAG],
            "head" : self._items,
            "data" : data,
            "hidden" : self._ignore_items,
            "filter" : self._filter_items,
            "format" : self.get_template_format(),
            "default_sort" : self.get_default_sort(),
            "bottom_static" : self.get_bottom_static(),
            "tips" : self.get_help_tips()
        }
        return result

    def get_kendo_data(self):
        url_args = self.get_url_args()
        cpid = url_args['cpid']
        m_cpid = int(url_args['m_cpid'])

        data = [(date_str, [dd for dd in d[self.tag].get(cpid, []) if dd['redirects']]) for date_str, d in self._result_map if d]
        d = self.join_website_report(data, m_cpid)
        data = calc(d)

        warn_result = self.init_warn_result(data)
        api_args = {"type":"target", "action":["pause", "resume"]}
        result = {
            "tag" : table_tag_config[ZEROPARK_TARGET_TAG],
            "head" : self._items,
            "data" : data,
            "hidden" : self._ignore_items,
            "filter" : self._filter_items,
            "format" : self.get_template_format(),
            "default_sort" : self.get_default_sort(),
            "bottom_static" : self.get_bottom_static(),
            "tips" : self.get_help_tips(),
            "api_args" : api_args
        }
        return [result, warn_result]

    def join_website_report(self, data, m_cpid):
        ret = {}
        for date_str, api_reports in data:
            tmp_reports = self.get_massival_report(date_str, 'websiteid', tar_prefix="websiteid_%s_"%m_cpid, ssdb_key_prefix="_websiteBid_%s_"%m_cpid)
            massival_report = {}
            n = 0
            for r in tmp_reports:
                if r['cpid'] != m_cpid:
                    continue

                if r['websiteid'] not in massival_report:
                    massival_report[r['websiteid']] = r
                else:
                    for k, v in r.items():
                        if k in ['visits', 'clicks', 'conversions', 'cost', 'revenue', 'profit']:
                            massival_report[r['websiteid']][k] += v
            for r in api_reports:
                rpt = massival_report.get(r['target'], {})
                r['m_revenue'] = rpt.get('revenue', 0.0)
                r['m_clicks'] = rpt.get('clicks', 0)
                r['m_visits'] = rpt.get('visits', 0)
                r['m_convs'] = rpt.get('conversions', 0)
                r['m_cost'] = rpt.get('cost', 0)
                r['profit'] = r['m_revenue'] - r['spent']
                if self.is_crypt_user():
                    r['target'] = self.crypto(r['target'])
        return data

class ZeroParkApiOpRec(BaseResult):
    def __init__(self):
        super(ZeroParkApiOpRec, self).__init__()
        self._add_template_format("clicks", "n0")
        self._add_template_format("redirects", "n0")
        self._add_template_format("spent", "c2")
        keys = ['target', 'clicks', 'redirects', 'spent', 'op', 'time']
        self.set_items(keys)
        self.set_sort_default([[5, 'desc']])

    def load_result(self):
        pass

    def get_data_rec(self, target, info):
        res = {'target': target}
        res.update(info)
        if self.is_crypt_user():
            res['target'] = self.crypto(res['target'])
        if res.get('time'):
            res['time'] = ts_to_str_min(res['time'])
        else:
            res['time'] = ""
        return res

    def get_kendo_data(self):
        url_args = self.get_url_args()
        cur_cpid = url_args['cpid']

        data = []
        uid = self.get_uid()
        cache = get_zp_op_cache(uid)
        for cpid, targets in cache.items():
            if cpid != cur_cpid:
                continue
            for target, info in targets.items():
                rec = self.get_data_rec(target, info)
                data.append(rec)


        result = {
            "head" : self._items,
            "data" : data,
            "hidden" : self._ignore_items,
            "filter" : self._filter_items,
            "format" : self.get_template_format(),
            "default_sort" : self.get_default_sort(),
            "bottom_static" : self.get_bottom_static(),
            "tips" : self.get_help_tips()
        }
        return result

class RelativeEventOfferReportResult(BaseResult):
    def __init__(self):
        super(RelativeEventOfferReportResult, self).__init__()
        items = ['Date', 'Offer', 'Type', 'Conv', 'Description']
        self.set_items(items)
        self.add_items(['oid'])
        json_keys = [
            {"key":"oid", "class" : AdminOffer, "is_rule":False, "admin_uid":-1},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('relative_offer')
        self.set_sort_default([[0,'desc'],[1,'asc']])
        self.add_filter_items('Offer', 'contains')
        self.add_filter_items('Date', 'contains')
        self.add_filter_items('Type', 'contains')
        self.finish_init()
        self.set_prefix_filename("event_")

    def set_uid(self, uid):
        super(RelativeEventOfferReportResult, self).set_uid(uid)
        permission = self.get_user_permission(uid)
        if permission == 8:
            self._uid = 57 ## bd

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for oid, info in objs.items():
                if oid not in self._result_map:
                    self._result_map[oid] = {}
                for key, _data  in info.items():
                    if key not in self._result_map[oid]:
                        self._result_map[oid][key] = {}
                    for f, obj in _data.items():
                        self._result_map[oid][key][f] = obj

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        for oid, keyObj in self._result_map.items():
            for key, info in keyObj.items():
                for t, obj in info.items():
                    conv, visits, description, ts = obj
                    items = []
                    time_str = ts_to_str_min(ts)
                    items.append(time_str)
                    oid_name = names_map["oid"].get(int(oid), str(oid))
                    items.append(oid_name)
                    items.append(key)
                    items.append(conv)
                    #items.append(visits)
                    items.append(description)
                    items.append(oid)
                    self._result_list.append(items)

        return self._result_list

class RelativeEventValveOfferReportResult(BaseResult):
    def __init__(self):
        super(RelativeEventValveOfferReportResult, self).__init__()
        items = ['Date', 'Offer', 'Type', 'Conv', 'Description']
        self.set_items(items)
        self.add_items(['oid'])
        json_keys = [
            {"key":"oid", "class" : AdminOffer, "is_rule":False, "admin_uid":-1},
        ]
        self.add_json_keys(json_keys)
        self.set_tag('relative_valve_offer')
        self.set_sort_default([[0,'desc'],[1,'asc']])
        self.add_filter_items('Offer', 'contains')
        self.add_filter_items('Date', 'contains')
        self.add_filter_items('Type', 'contains')
        self.finish_init()
        self.set_prefix_filename("event_")

    def set_uid(self, uid):
        super(RelativeEventValveOfferReportResult, self).set_uid(uid)
        permission = self.get_user_permission(uid)
        if permission == 8:
            self._uid = 57 ## bd

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for oid, info in objs.items():
                if oid not in self._result_map:
                    self._result_map[oid] = {}
                for key, _data  in info.items():
                    if key not in self._result_map[oid]:
                        self._result_map[oid][key] = {}
                    for f, obj in _data.items():
                        self._result_map[oid][key][f] = obj

    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        for oid, keyObj in self._result_map.items():
            for key, info in keyObj.items():
                for t, obj in info.items():
                    conv, visits, description, ts = obj
                    items = []
                    time_str = ts_to_str_min(ts)
                    items.append(time_str)
                    oid_name = names_map["oid"].get(int(oid), str(oid))
                    items.append(oid_name)
                    items.append(key)
                    items.append(conv)
                    #items.append(visits)
                    items.append(description)
                    items.append(oid)
                    self._result_list.append(items)
        return self._result_list

class PropellerReport(BaseResult):
    def __init__(self):
        super(PropellerReport, self).__init__()
        self._api_report_file_path = settings.propeller_json_dir

        self._add_template_format("cost", "c2")
        self._add_template_format("profit", "c2")
        self._add_template_format("m_revenue", "c2")
        self._add_template_format("m_visits", "n0")
        self._add_template_format("m_clicks", "n0")
        self._add_template_format("m_convs", "n0")
        self._add_template_format("show", "n0")
        self._add_template_format("click", "n0")
        self._add_template_format("convers", "n0")

    def calc_higher_order_args(self, rec):
        if 'show' in rec and rec['show'] != 0:
            rec['CTR'] = rec.get('m_clicks', 0) * 1.0 /rec['show']
            rec['CPM'] = rec.get('cost', 0.0)/rec['show'] * 1000
            rec['EPM'] = rec.get('m_revenue', 0)/rec['show'] * 1000
        else:
            rec['CTR'] = 0
            rec['CPM'] = 0
            rec['EPM'] = 0
        if 'cost' in rec and rec['cost'] != 0:
            rec['ROI'] = (rec.get('m_revenue', 0.0) * 1.0 - rec['cost'])/rec['cost']
        else:
            rec['ROI'] = 0.0

    def get_propeller_file_path(self, datetime_str):
        file_path = osp.join(self._api_report_file_path, str(self.get_uid()))
        return osp.join(file_path, "%s.json"%datetime_str)

    def load_result(self):
        range_days = self.get_range_days()
        start_day = self.get_start_day()
        self.cache = {}
        self._result_map = []
        for i in xrange(range_days):
            cur_dt = datetime.datetime.fromtimestamp(start_day+ i*ONE_DAY_SECONDS)
            datetime_str = cur_dt.strftime('%Y%m%d')
            ts = str_day_to_ts(datetime_str)
            file_path = self.get_propeller_file_path(datetime_str)
            key = self.get_propeller_mss_db_key(ts)
            data = self.get_cache(key)
            if not data or self.check_propeller_file_is_modify(file_path, datetime_str):
                data = self.get_propeller_data_from_file(file_path)
                self.set_propeller_data_cache(data, datetime_str, ts)
            self._result_map.append((datetime_str, data))

    def set_propeller_data_cache(self, data, file_name, ts):
        file_path = self.get_propeller_file_path(file_name)
        last_time = self.get_file_modify_time(file_path)
        if last_time != -1:
            self.set_cache(self.get_propeller_mss_cachetime_key(file_name), last_time, ts)

        s_key = self.get_propeller_mss_db_key(ts)
        self.set_cache(s_key, json.dumps(data), ts)

    def check_propeller_file_is_modify(self, path, file_name):
        last_time = self.get_file_modify_time(path)
        cache_time = self.get_cache(self.get_propeller_mss_cachetime_key(file_name))
        if cache_time is None:
            cache_time = -1
        return cache_time != last_time

    def is_crypt_user(self):
        user = DBSet.get_db_client().select_one(User, id=self._raw_uid)
        return check_permission(PERMISSION_REPORT, user.permission, PERMISSION_REPORT_ZERO_ENCRYPT)

    def get_propeller_mss_cachetime_key(self, file_name):
        return "propeller_%s_0_%s" % (self.get_uid(), file_name)

    def get_propeller_mss_db_key(self, ts):
        return "propeller_%s_0_common_%s" % (self.get_uid(), ts)

    def get_propeller_data_from_file(self, file_path):
        data = None
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                s = "".join(lines)
                s = decode_from_utf8(s)
                data = json.loads(s)
        except Exception, ex:
            print ex
        return data

    def finish_init(self):
        formats = {
            "profit" : {"reg":"$"},
            "ROI" : {"reg":"%"}
            }
        self.add_column_format(formats)

    def add_column_format(self, formats):
        cols = self.__find_columns_by_names(formats.keys())
        for k, v in cols.items():
            tmp = {
                "col" : v,
                "reg" : formats[k]["reg"]
            }
            self._format_columns.append(tmp)

    def __find_columns_by_names(self, names):
        res = {}
        for k in names:
            for i in xrange(len(self._pp_items)):
                if k == self._pp_items[i]:
                    res[k] = i
        return res



class PropellerCampReport(PropellerReport):
    def __init__(self):
        super(PropellerCampReport, self).__init__()
        self._pp_items = ["name", "campaign_id", 'm_cpid', "cost", "profit",  "m_revenue", "m_visits", "m_clicks", "m_convs", "show", 'ROI', 'CTR', 'EPM', 'CPM']
        self.set_tag('campaign')
        self._ignore_items = [1, 2]
        self._filter_items = {0:"contains"}
        #self.set_sort_default([[6,'desc']])
        self.finish_init()


    def join_massival_report(self, data, massival_data):
        for d in data:
            s = "#(%s)#"%d['campaign_id']
            d['m_cpid'] = 0
            d['name'] = d['campaign_id']
            for md in massival_data:
                name = md['Campaign']
                if name.startswith("Propeller") and s in name:
                    d['name'] = md['Campaign']
                    d['m_cpid'] = md['cpid']
                    d['m_revenue'] = md['Revenue']
                    d['m_visits'] = md['Visits']
                    d['m_clicks'] = md['Clicks']
                    d['m_convs'] = md['Convs']
                    d['profit'] = d['m_revenue'] - d['cost']
                    self.calc_higher_order_args(d)
                    break
        return

    def get_kendo_data(self):
        data = [(ds, d['campaign']) for ds, d in self._result_map if d]
        data = self.calc_data(data)
        massival_data = self.get_massival_camp_rep()
        self.join_massival_report(data, massival_data)
        result = {}
        result["head"] = self._pp_items
        result["data"] = data
        result["hidden"] = self._ignore_items
        result["filter"] = self._filter_items
        result["format"] = self.get_template_format()
        result["default_sort"] =  self.get_default_sort()
        result["bottom_static"] = self.get_bottom_static()
        result["tips"] = self.get_help_tips(),
        return result

    def get_massival_camp_rep(self):
        self._result_map = {}
        self.insert_items(['Campaign'])
        self.add_items(['cpid'])
        self.add_json_keys([{"key":"cpid", "class":Campaign, "is_rule":False}])
        result = []
        self.set_timezone(-5)
        super(PropellerReport, self).load_result()
        raw_data = self.get_raw_data()
        result = []
        for d in raw_data:
            tmp = {}
            for i in xrange(len(d)):
                tmp[self._items[i]] = d[i]
            result.append(tmp)
        return result

    def get_raw_custom_data(self, filter_col=None):
        result = {}
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            cpid = key_list[0]
            if cpid not in result:
                result[cpid] = {}
            items = []
            for k in self._custom_head:
                v = getattr(_result, k)
                items.append(v)
            result[cpid] = items
        return result

    def calc_data(self, data):
        ret = {}
        for _, v in data:
            for d in v:
                if d['campaign_id'] not in ret:
                    ret[d['campaign_id']] = d
                else:
                    ret[d['campaign_id']]['show'] += d['show']
                    ret[d['campaign_id']]['cost'] += d['cost']
                    ret[d['campaign_id']]['click'] += d['click']
                    ret[d['campaign_id']]['convers'] += d['convers']
        return ret.values()

class PropellerZoneReport(PropellerReport):
    def __init__(self):
        super(PropellerZoneReport, self).__init__()
        self._pp_items = ["Website", "cost", "profit",  "m_revenue", "m_visits", "m_clicks", "m_convs", "show", 'ROI', 'CTR', 'EPM', 'CPM']
        self.set_tag('websiteid')
        self._filter_items = {0:"contains"}
        #self.set_sort_default([[6,'desc']])
        self.finish_init()

    def join_massival_report(self, data, massival_data):
        for d in data:
            d['Website'] = d['zone_id']
            d.pop('zone_id')
            for md in massival_data:
                if d['Website'] == md['Website']:
                    d['m_revenue'] = md['Revenue']
                    d['m_visits'] = md['Visits']
                    d['m_clicks'] = md['Clicks']
                    d['m_convs'] = md['Convs']
                    d['profit'] = d['m_revenue'] - d['cost']
                    self.calc_higher_order_args(d)
                    break
        return


    def get_kendo_data(self):
        data = [(ds, d['zone']) for ds, d in self._result_map if d]
        data = []
        url_args = self.get_url_args()
        cpid = url_args.get('cpid', '')
        for ds, d in self._result_map:
            if not d:
                continue
            d = d.get('zone', {}).get(cpid)
            if not d:
                continue
            data.append((ds, d))

        data = self.calc_data(data)
        data.sort(key=lambda e:e['show'])
        data = data[-500 if len(data) >= 500 else -len(data):]
        data.reverse()
        mss_data = self.get_massival_website_rep()
        self.join_massival_report(data, mss_data)
        result = {
            "head" : self._pp_items,
            "data" : data,
            "hidden" : self._ignore_items,
            "filter" : self._filter_items,
            "format" : self.get_template_format(),
            "default_sort" :  self.get_default_sort(),
            "bottom_static" : self.get_bottom_static(),
            "tips" : self.get_help_tips()
        }
        return result

    def get_massival_website_rep(self):
        self._result_map = {}
        self.insert_items(['Campaign', 'Website'])
        self.add_items(['cpid', 'websiteid'])
        json_keys = [
            {"key":"cpid", "class":Campaign, "is_rule":True},
            {"key":"websiteid", "class":None, "is_rule":False, "add_ignore":True},
        ]
        url_args = self.get_url_args()
        self._rules['cpid'] = int(url_args['m_cpid'])

        self.add_json_keys(json_keys)
        self.set_tar_prefix_name("websiteid_%s_" % (url_args['m_cpid']))

        result = []
        self.set_timezone(-5)
        super(PropellerReport, self).load_result()
        raw_data = self.get_raw_data()
        for d in raw_data:
            tmp = {}
            for i in xrange(len(d)):
                tmp[self._items[i]] = d[i]
            result.append(tmp)
        return result

    def calc_data(self, data):
        ret = {}
        is_crypt = self.is_crypt_user()
        for _, v in data:
            for d in v:
                if d['zone_id'] not in ret:
                    ret[d['zone_id']] = d
                else:
                    ret[d['zone_id']]['show'] += d['show']
                    ret[d['zone_id']]['cost'] += d['cost']
                    ret[d['zone_id']]['click'] += d['click']
                    ret[d['zone_id']]['convers'] += d['convers']
        if is_crypt:
            for _, v in ret.items():
                v['zone_id'] = self.crypto(str(v['zone_id']))
        return ret.values()


    def get_raw_data(self, filter_col=None):
        names_map = self.find_name_map(self._json_keys)
        result_list = []
        is_crypt = self.is_crypt_user()
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()
            for i in range(len(key_list)-1, -1,-1):
                k = key_list[i]
                jk_k = self._json_keys[i].get("key", None)
                if is_crypt:
                    if jk_k == "websiteid" and str(k) != "":
                        k = self.crypto(str(k))
                if jk_k and jk_k in names_map:
                    name = names_map[jk_k].get(k, "%s"%k)
                    items.insert(0, name)
                else:
                    items.insert(0, k)
            if self._is_show_date:
                dt = ts_to_date(ts)
                datetime_str = dt.strftime('%Y%m%d')
                items = _result.to_raw_items()
                items.insert(0, datetime_str[4:])

            for i in xrange(len(key_list)):
                if self._json_keys[i].get("add_ignore", None):
                    continue
                k = key_list[i]
                items.append(k)
            if filter_col:
                filter_items = []
                for col in filter_col:
                    filter_items.append(items[col])
                items = filter_items
            result_list.append(items)
        return result_list


class PropellerCampDateReport(PropellerReport):
    def __init__(self):
        super(PropellerCampDateReport, self).__init__()
        self._pp_items = ['Date', "name", "campaign_id", 'm_cpid', "cost", "profit",  "m_revenue", "m_visits", "m_clicks", "m_convs", "show", 'ROI', 'CTR', 'EPM', 'CPM']
        self.set_tag('campaign')
        self._ignore_items = [2, 3]
        self._filter_items = {0:"contains"}
        #self.set_sort_default([[6,'desc']])
        self.finish_init()

    def join_massival_report(self, data, massival_data):
        for d in data:
            for md in massival_data:
                d['m_cpid'] = 0
                if d['Date'] != md['Date']:
                    continue
                name = md['Campaign']
                d['name'] = md['Campaign']
                d['m_cpid'] = md['cpid']
                d['m_revenue'] = md['Revenue']
                d['m_visits'] = md['Visits']
                d['m_clicks'] = md['Clicks']
                d['m_convs'] = md['Convs']
                d['profit'] = d['m_revenue'] - d['cost']
                self.calc_higher_order_args(d)
                break
        return

    def get_kendo_data(self):
        url_args = self.get_url_args()
        m_cpid = url_args['m_cpid']
        cpid = url_args['cpid']
        data = [(ds, d['campaign']) for ds, d in self._result_map if d]
        data = self.filter_data(data, cpid)
        massival_data = self.get_massival_camp_rep()
        self.join_massival_report(data, massival_data)
        result = {}
        result["head"] = self._pp_items
        result["data"] = data
        result["hidden"] = self._ignore_items
        result["filter"] = self._filter_items
        result["format"] = self.get_template_format()
        result["default_sort"] =  self.get_default_sort()
        result["bottom_static"] = self.get_bottom_static()
        result["tips"] = self.get_help_tips(),
        return result

    def get_massival_camp_rep(self):
        self._result_map = {}
        self.insert_items(['Date', 'Campaign'])
        self.add_items(['cpid'])
        self.add_json_keys([{"key":"cpid", "class":Campaign, "is_rule":False}])

        url_args = self.get_url_args()
        self._rules['cpid'] = int(url_args['m_cpid'])

        self.set_timezone(-5)
        super(PropellerReport, self).load_result()
        raw_data = self.get_raw_data()
        result = []
        for d in raw_data:
            tmp = {}
            for i in xrange(len(d)):
                tmp[self._items[i]] = d[i]
            result.append(tmp)
        return result

    def filter_data(self, data, cpid):
        ret = []
        for ds, v in data:
            for d in v:
                if d['campaign_id'] == cpid:
                    d['Date'] = ds
                    ret.append(d)
                    break
        return ret

    def load_offset_result(self):
        self.load_base_offset_result()

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        ret = []
        if objs:
            for obj in objs:
                cpid = obj.get('cpid', None)
                if cpid is not None and self.is_valid_rules({"cpid":cpid}):
                    if ts not in self._result_map:
                        self._result_map[ts] = len(self._result_list)
                        self._result_list.append((ts, cpid, StatResult()))

                    index = self._result_map[ts]
                    self._result_list[index][2].add_raw(obj)

    def get_raw_data(self, filter_col=None):
        raw_list = []
        names_map = self.get_cpnames() or self.get_db_record_names(Campaign, uid=self.get_uid())
        for ts, cpid, _result in self._result_list:
            items = _result.to_raw_items()
            cpid_name = names_map.get(cpid, "%s" % (cpid))
            items.insert(0, cpid_name)
            dt = ts_to_date(ts)
            datetime_str = dt.strftime('%Y%m%d')
            items.insert(0, datetime_str)
            items.append(cpid)
            raw_list.append(items)
        return raw_list


