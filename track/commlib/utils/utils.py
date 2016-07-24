#!/usr/bin/env python
# -*- coding:utf-8 -*-

import locale

import time
import datetime

locale.setlocale(locale.LC_ALL, "en_US")

DAY_TYPE_FULL = 0
DAY_TYPE_PART = 1
ONE_DAY_SECONDS = 3600 * 24
ONE_HOUR_SECONDS = 3600
TIMEZONE = -time.timezone / 3600

def format_int_comma(v, args=None):
    return locale.format("%d", v, grouping=True)

def format_float_comma(v, args=None):
    return locale.format("%.2f", v, grouping=True)

def format_str(v, args=None):
    return locale.format("%s", v, grouping=True)

def str_to_date(s):
    return datetime.datetime.strptime(s, '%Y%m%d%H')


def date_to_ts(dt):
    return int(time.mktime(dt.timetuple()))


def ts_to_date(ts):
    return datetime.datetime.fromtimestamp(ts)

class LoadTimeList(object):
    def __init__(self, start_day, range_days, timezone):
        self.start_day = start_day
        self.range_days = range_days
        self.timezone = timezone

    def _merge_list(self, a, b):
        for i in b:
            a.append(i)
        return a

    def get_offset_timezone(self):
        return (TIMEZONE - self.timezone) * 3600

    def _get_first_offset_hour(self):
        start_hour = (TIMEZONE - self.timezone) % 24
        end_hour = 24
        return start_hour, end_hour

    def _get_last_offset_hour(self):
        start_hour = 0
        end_hour = (TIMEZONE - self.timezone) % 24
        return start_hour, end_hour

    def _do_load_first_offset_day(self,start_day, range_days):
        start_hour, end_hour = self._get_first_offset_hour()
        offset_ts = start_day + self.get_offset_timezone()
        return self.load_part_day_list(offset_ts, start_hour, end_hour)

    def _do_load_last_offset_day(self, start_day, range_days):
        start_hour, end_hour = self._get_last_offset_hour()
        if self.timezone > TIMEZONE:
            range_days = range_days - 1
        cur_dt = datetime.datetime.fromtimestamp(start_day + range_days*ONE_DAY_SECONDS)
        ts = date_to_ts(cur_dt)
        return self.load_part_day_list(ts, start_hour, end_hour)

    def load_time_list(self):
        if self.timezone == TIMEZONE:
            return self.load_origin()
        else:
            return self.load_offset()

    def load_origin(self):
        return self.load_full_day_list(self.start_day, self.range_days)

    def load_offset(self):
        range_days = self.range_days
        start_day = self.start_day

        result = []
        tmp = self._do_load_first_offset_day(start_day, range_days)
        self._merge_list(result, tmp)
        tmp = self._do_load_last_offset_day(start_day, range_days)
        self._merge_list(result, tmp)
        if range_days > 1:
            if self.timezone < TIMEZONE:
                start_day = start_day + ONE_DAY_SECONDS
            tmp = self.load_full_day_list(start_day, range_days-1)
            self._merge_list(result, tmp)
        return result

    def load_full_day_list(self, start_day, range_days):
        result = []
        for i in xrange(range_days):
            cur_dt = datetime.datetime.fromtimestamp(start_day+ i*ONE_DAY_SECONDS)
            date_str = cur_dt.strftime('%Y%m%d')
            result.append((date_str, DAY_TYPE_FULL))
        return result

    def load_part_day_list(self, start_ts, from_hour=0, to_hour=24):
        result = []
        for i in xrange(0, to_hour-from_hour, 1):
            hour_dt = datetime.datetime.fromtimestamp(start_ts + i*ONE_HOUR_SECONDS)
            hour_str = hour_dt.strftime('%Y%m%d%H')
            result.append((hour_str, DAY_TYPE_PART))
        return result

def toCharCode(s):
    encode = ','.join([str(ord(s[i])) for i in xrange(len(s))])
    return encode
    
