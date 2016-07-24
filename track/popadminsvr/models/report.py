#!/usr/bin/env python
# -*- coding:utf-8 -*-
from os import path as osp
import time
import datetime
import ujson as json
import tarfile

from global_vars import global_db_set as DBSet
from stat_result import StatResult
from db_client import *
from utils import TIMEZONE, ONE_DAY_SECONDS
from config.table_config import ALL_TAGS, RULES_NO_LENGTH_LIMIT, STATIC_DATA_BY_DAY, STATIC_DATA_BY_HOUR, IGNORE_RULE_ID
from config.table_config import FORMAT_INT, FORMAT_DOLLAR_TWO, FORMAT_DOLLAR_THREE, FORMAT_PERCENT
from commlib.utils.utils import ONE_HOUR_SECONDS
from utils import decode_from_utf8

import settings

__SUFFIX__ = "txt"

BID_DIR = "bid"
ONE_HOUR_SECOND = 3600

class BaseResult(object):
    def __init__(self):
        self._items = []
        self._fields = []


        self._dashboard_head = []
        self._chart_head = []
        self._sort_default = []
        self._result_list = []
        self._result_map = {}

        self._tag = 'all'
        self._uid = 0
        self._user_name = ""

        self._start_day = 0
        self._end_day = 0
        self._start_hour = 0
        self._end_hour = 23
        self.__init_day()
        self._args = {}

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
        #self.__init_template_format()

        self._prefix_filename = ""
        self._tar_prefix_filename = ""
        self._hour_data = {}


        self.init_template_format()

    def init_template_format(self):
        self.__add_template_format("Bids", FORMAT_INT)
        self.__add_template_format("Views", FORMAT_INT)
        self.__add_template_format("Visits", FORMAT_INT)
        self.__add_template_format("Clicks", FORMAT_INT)
        self.__add_template_format("Cost", FORMAT_DOLLAR_TWO)
        self.__add_template_format("CPM", FORMAT_DOLLAR_THREE)
        self.__add_template_format("EPM", FORMAT_DOLLAR_THREE)
        self.__add_template_format("Profit", FORMAT_DOLLAR_TWO)
        self.__add_template_format("ROI", FORMAT_PERCENT)
        self.__add_template_format("Convs", FORMAT_INT)
        self.__add_template_format("CTR", FORMAT_PERCENT)
        self.__add_template_format("CPC", FORMAT_DOLLAR_THREE)
        self.__add_template_format("CR", FORMAT_DOLLAR_THREE)
        self.__add_template_format("WR", FORMAT_PERCENT)
        self.__add_template_format("Revenue", FORMAT_DOLLAR_TWO)
        self.__add_template_format("bid", FORMAT_DOLLAR_THREE)
        self.__add_template_format("BudgetRate", "custom")
        self.__add_template_format("CBudget", "custom")

    def set_hour(self, s, e):
        self._start_hour, self._end_hour = s, e

    def ts_to_str_day(self, ts):
        x = time.localtime(ts)
        return time.strftime("%Y%m%d", x)

    def ts_to_ts_day(self, ts):
        ts_str = self.ts_to_str_day(ts)
        return self.str_day_to_ts(ts_str)

    def get_hour(self):
        return self._start_hour, self._end_hour

    def str_to_date(self, s):
        return datetime.datetime.strptime(s, '%Y%m%d%H')

    def date_to_ts(self, dt):
        return int(time.mktime(dt.timetuple()))

    def ts_to_date(self, ts):
        return datetime.datetime.fromtimestamp(ts)

    def str_day_to_ts(self, s):
        dt = datetime.datetime.strptime(s, "%Y%m%d")
        return self.date_to_ts(dt)

    def str_hour_to_ts(self, s):
        dt = datetime.datetime.strptime(s, "%Y%m%d%H")
        return self.date_to_ts(dt)

    def ts_to_str_min(self, ts):
        x = time.localtime(ts)
        return time.strftime("%Y-%m-%d %H:%M", x)

    def ts_to_str_hour(self, ts):
        x = time.localtime(ts)
        return time.strftime("%Y%m%d%H", x)

    def get_kendo_charts(self):
        return []

    def get_offset_timezone(self):
        return (TIMEZONE - self._timezone) * 3600

    def __add_template_format(self, k, v):
        self._template_format[k] = v

    def get_template_format(self):
        return self._template_format

    def set_timezone(self, timezone):
        self._timezone = timezone

    def get_timezone(self):
        return self._timezone

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

    def get_all_uids(self):
        res = DBSet.get_db_client().select_all(User)
        uids = []
        for obj in res:
            uids.append((obj.id, obj.name))
        return uids

    def __find_columns_by_names(self, names):
        res = {}
        for k in names:
            for i in xrange(len(self._fields)):
                item = self._fields[i]
                item = item['field'] if type(item) == dict else item
                if k == item:
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

    def get_ignore_items(self):
        return self._ignore_items

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
        return  "%s%s.%s" % (self.get_prefix_filename(), file_name, __SUFFIX__)

    def get_day_file_path(self):
        return osp.join(settings.json_dir, str(self.get_uid()), BID_DIR)

    def get_hour_file_path(self):
        return osp.join(settings.json_dir, str(self.get_uid()), BID_DIR, "hour")

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
        return "%s_%s_%s_%s_%s" % (self.get_prefix_filename(), self.get_uid(), data_type, tag, ts)

    def get_mss_cachetime_key(self, file_name):
        is_full_day = self.get_full_day()
        data_type = 0 if is_full_day else 1
        return "%s_%s_%s_%s" % (self.get_prefix_filename(), self.get_uid(), data_type, file_name)

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
            if self.get_data_type() == STATIC_DATA_BY_DAY:
                if self.get_full_day():
                    key_ts = self.str_day_to_ts(key)
                else:
                    key_ts = self.str_hour_to_ts(key)
            elif self.get_data_type() == STATIC_DATA_BY_HOUR:
                key_ts = self.str_hour_to_ts(key)
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
        #data = self.get_cache(key)
        data = None
        file_path = self._do_get_file_path(file_name)
        file_full_name = self._get_file_full_name(file_name)
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
        cur_dt = self.ts_to_date(ts)
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
            #tarObj = tarfile.open(file_path, "r:*")
            #obj = tarObj.getmember(file_name)
            #f = tarObj.extractfile(obj)
            f = open(file_path, "r:*")
            lines = f.readlines()
            s = "".join(lines)
            s = decode_from_utf8(s)
            data = json.loads(s)
            return data
        except Exception, ex:
            print "%s : %s"%(ex, data)
        return data

    def find_ins_map(self, keys):
        names_map = {}
        for _info in keys:
            key = _info.get("key", None)
            ins = _info.get("class", None)
            handler = _info.get("handler", None)
            if not key or not ins:
                continue
            tmp = self.get_db_record(ins, uid=self.get_uid())
            names_map[key] = tmp
        return names_map

    def find_name_map(self, keys):
        names_map = {}
        for _info in keys:
            key = _info.get("key", None)
            ins = _info.get("class", None)
            handler = _info.get("handler", None)
            if not key or not ins:
                continue
            if key == "cpid":
                tmp = self.get_cpnames() or self.get_db_record_names(ins, uid=self.get_uid())
            elif key == "banner":
                camps = DBSet.get_db_client().select_all(ins, uid=self.get_uid())
                tmp = [camp.iamge_urls.split(",") for camp in camps]
            else:
                tmp = self.get_db_record_names(ins, uid=self.get_uid())
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

    def is_offset_date(self):
        return not self.is_origin_timezone() or self._start_hour != 0 or self._end_hour != 23

    def is_origin_timezone(self):
        return self._timezone == TIMEZONE

    #def load_base_offset_result(self):
    #    self.set_full_day(False)
    #    range_days = self.get_range_days()
    #    start_day = self.get_start_day()
    #    offset_ts = start_day + self.get_offset_timezone()
    #    for i in xrange(range_days):
    #        s = offset_ts + i * ONE_DAY_SECONDS
    #        c = start_day + i * ONE_DAY_SECONDS
    #        for j in xrange(24):
    #            cur_dt = datetime.datetime.fromtimestamp(s+ j*ONE_HOUR_SECONDS)
    #            datetime_str = cur_dt.strftime('%Y%m%d%H')
    #            ts = self.date_to_ts(cur_dt)
    #            self.static_result(datetime_str, ts, c)

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
            day_ts = self.ts_to_ts_day(c)
            hour_dt = datetime.datetime.fromtimestamp(s)
            datetime_str = hour_dt.strftime('%Y%m%d%H')
            ts = self.date_to_ts(hour_dt)
            self.static_result(datetime_str, ts, day_ts)



    def load_result(self):
        if not self.is_offset_date():
            self.load_origin_result()
        else:
            self.load_offset_result()

    def load_origin_result(self):
        range_days = self.get_range_days()
        start_day = self.get_start_day()
        self.load_full_day(start_day, range_days)

    def load_full_day(self, start_day, range_days):
        self.set_full_day(True)
        for i in xrange(range_days):
            cur_dt = datetime.datetime.fromtimestamp(start_day+ i*ONE_DAY_SECONDS)
            datetime_str = cur_dt.strftime('%Y%m%d')
            ts = self.date_to_ts(cur_dt)
            self.static_result(datetime_str, ts, ts)

    def load_part_day(self, offset_ts, key_ts, from_hour=0, to_hour=23, save_hour_data=False):
        self.set_full_day(False)
        n = 0
        to_hour += 1
        for j in xrange(0, to_hour-from_hour, 1):
            hour_dt = datetime.datetime.fromtimestamp(offset_ts + j*ONE_HOUR_SECONDS)
            datetime_str = hour_dt.strftime('%Y%m%d%H')
            h_ts = self.date_to_ts(hour_dt)
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
        diff_ts = self.date_to_ts(diff_dt)
        return diff_ts

    def _get_first_offset_hour(self):
        start_hour = (TIMEZONE - self._timezone) % 24
        end_hour = 24
        return start_hour, end_hour

    def _get_last_offset_hour(self):
        start_hour = 0
        end_hour = (TIMEZONE - self._timezone) % 24
        return start_hour, end_hour

    def _do_load_first_offset_day(self,start_day, range_days):
        start_hour, end_hour = self._get_first_offset_hour()
        cur_dt = datetime.datetime.fromtimestamp(start_day)
        ts = self.date_to_ts(cur_dt)
        offset_ts = start_day + self.get_offset_timezone()
        self.load_part_day(offset_ts, ts, start_hour, end_hour)

    def _do_load_last_offset_day(self, start_day, range_days, save_hour_data=False):
        start_hour, end_hour = self._get_last_offset_hour()
        if self._timezone > TIMEZONE:
            range_days = range_days - 1
        cur_dt = datetime.datetime.fromtimestamp(start_day + range_days*ONE_DAY_SECONDS)
        ts = self.date_to_ts(cur_dt)
        return self.load_part_day(ts, ts, start_hour, end_hour, save_hour_data)

    def _cal_range_days(self, start_ts, end_ts):
        s_ts = self.ts_to_ts_day(start_ts)
        e_ts = self.ts_to_ts_day(end_ts)
        diff_day = (e_ts - s_ts) / ONE_DAY_SECONDS
        return diff_day

    def _cal_day_range_ts(self):
        offset_start_hour = (TIMEZONE - self._timezone + self._start_hour)
        offset_end_hour = (TIMEZONE - self._timezone + self._end_hour)
        start_ts = self.get_start_day() + offset_start_hour * ONE_HOUR_SECOND
        end_ts = self.get_end_day() + offset_end_hour * ONE_HOUR_SECOND
        return start_ts, end_ts

    def load_offset_result(self):
        start_hour, end_hour = self.get_hour()
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
            for cpid, obj in objs.iteritems():
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

    def handle_extra_items(self, key_list, ins_map):
        ret = []
        for i in xrange(len(key_list)):
            k = key_list[i]
            jk_k = self._json_keys[i].get("key", None)
            jk_h = self._json_keys[i].get("handler", None)
            if jk_k:
                if jk_k in ins_map:
                    ins = ins_map[jk_k].get(int(k), None)
                    if ins:
                        res =  jk_h(id=int(k), ins=ins) if jk_h else ins.name
                    else:
                        res = "%s"%k
                    ret.append(res)
                else:
                    ret.append("%s"%k)

            else:
                ret.append(k)
        return ret

    def get_raw_data(self, filter_col=None):
        ins_map = self.find_ins_map(self._json_keys)
        result_list = []
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()

            items = self.handle_extra_items(key_list, ins_map) + items

            if self._is_show_date:
                dt = self.ts_to_date(ts)
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
            item = self._items[col]
            name = item['name'] if type(item) == dict else item
            result.append((name, op))
        return result

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
                item = self._items[cols[i]]
                item = item['name'] if type(item) == dict else item
                tmp[item] = d[i]
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

    def show_items(self, items):
        ignore = []
        for x in xrange(len(self._items)):
            item = self._items[x]
            item = item['name'] if type(item) == dict else item
            if item not in items:
                ignore.append(x)
        self._ignore_items = ignore
        self._fields = items

    def editable(self):
        return False

    def get_fields(self):
        return self._fields

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
        result['args'] = self._args
        for d in raw_data:
            tmp = {}
            for i in xrange(len(d)):
                item = self._items[i]
                if type(item) == dict:
                    item = item['name']
                tmp[item] = d[i]
            result["data"].append(tmp)
            if self.is_length_limit(result["data"]):
                break
        return result

    def get_kendo_async_data(self, *args, **kwargs):
        self.load_result()
        raw_data = self.get_raw_data()
        ret = []
        for d in raw_data:
            tmp = {}
            for i in xrange(len(d)):
                item = self._items[i]
                if type(item) == dict:
                    item = item['name']
                tmp[item] = d[i]
            ret.append(tmp)
            if self.is_length_limit(ret):
                break
        return ret

    def set_uid(self, uid):
        self._uid = uid

    def get_uid(self):
        return self._uid

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

    def set_start_day(self, start_day):
        self._start_day = start_day

    def get_start_day(self):
        return self._start_day

    def set_end_day(self, end_day):
        self._end_day = end_day

    def get_end_day(self):
        return self._end_day

    def get_edit(self):
        return False

    def get_range_days(self):
        return (self._end_day - self._start_day) / ONE_DAY_SECONDS + 1

    def get_toolbar(self, *args, **kwargs):
        return None

    def get_args(self, *args, **kwargs):
        return {}

    def parse_time(self, time_str):
        if ' ' in time_str:
            parts = time_str.split(' - ')
            start_dt = datetime.datetime.strptime(parts[0], "%m/%d/%Y")
            end_dt = datetime.datetime.strptime(parts[1], "%m/%d/%Y")
            if start_dt > end_dt:
                raise Exception('invalid start end time: %s %s' % (start_dt, end_dt))
            self._end_day = self.date_to_ts(end_dt)
            self._start_day = self.date_to_ts(start_dt)

    def get_db_record(self, class_inc, **kwargs):
        res = {}
        for ins in DBSet.get_db_client().select_all(class_inc, **kwargs):
            res[ins.id] = ins
        return res

    def get_db_record_names(self, class_inc, **kwargs):
        res = DBSet.get_db_client().select_all(class_inc, **kwargs)
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
        return None

    def init_data(self):
        pass

    def _match_payout(self, result, ts):
        ap = result["ap"]
        payout_list = result["payout_list"]
        last_payout = ap
        for i in xrange(len(payout_list)):
            payout, start_ts, timezone = payout_list[i]
            diff_ts = (timezone - TIMEZONE) * ONE_HOUR_SECONDS
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
            hour -= self.load_part_day(ts, ts, 0, 24, save_hour_data=True)

        if range_days:
            self.load_full_day(start_day, range_days)
        return


