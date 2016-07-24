#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime, time

from report import BaseResult
from db_client import Campaign
from stat_result import StatResult
from config import table_config
from utils import ONE_DAY_SECONDS
from commlib.utils.utils import ONE_HOUR_SECONDS
from global_vars import tmpl_reader, global_db_set as DBSet
import global_vars

class CampaignResult(BaseResult):
    def __init__(self):
        super(CampaignResult, self).__init__()
        self.set_items([
            'Campaign', 'CBudget', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'CPM', 'CTR', 'CR', 'CV', 'ROI',
            'EPM', 'EPC', 'AP', 'CPC', 'WR', 'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain', 'Orientation', 'Wid_typo',
            'Wid_digit', 'Errors', "Bids", 'cpid'
        ])
        self.add_json_keys([{"key":"cpid", "class":Campaign, "is_rule":False}])
        self.set_tag('campaign')
        self.set_sort_default([["Views", 'desc']])
        self.add_dashboard_head(['Campaign'])
        self.show_items(['Campaign', 'CBudget', 'WR', "Bids", 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'EPM', 'CPM', 'ROI', 'CTR', 'CPC', {'field':'cpid', 'hidden':True}])
        self.add_filter_items('Campaign', 'contains')
        self.finish_init()

    def get_bottom_static(self):
        result = {
            "Campaign":"Total",
            "CBudget":""
        }
        return result

    def init_data(self):
        self._init_rtb_campaigns(self.get_uid())
        self.__load_website_result()

    def _init_rtb_campaigns(self, uid):
        camps = DBSet.get_db_client().select_all(Campaign, uid=uid)
        self.rtb_campaigns = {}
        for o in camps:
            self.rtb_campaigns[o.id] = o

    def __load_website_result(self):
        from models.website_report import WebsiteResult
        rules = self.get_rules()
        timezone = self.get_timezone()
        start_day = self.get_start_day()
        end_day = self.get_end_day()
        uid = self.get_uid()

        ins = WebsiteResult()
        ins.set_uid(uid)
        ins.set_start_day(start_day)
        ins.set_end_day(start_day)
        ins.set_rules(rules)
        ins.set_timezone(timezone)
        ins.init_data()
        ins.load_result()
        self.website_result = ins.get_result_map()

    def _get_budget_notice_color(self, percent):
        if percent >=0.9:
            return "red"
        elif percent >= 0.8:
            return "orange"
        return "black"

    def get_template_format(self):
        return self._template_format

    def _calculate_budget(self, cpid, result_obj):
        if cpid not in self.rtb_campaigns:
            return 0
        cost = result_obj.cost
        budget = self.rtb_campaigns[cpid].daily_budget
        percent = cost*1.0/budget
        return percent

    def _calculate_website_budget(self, cpid):
        if cpid not in self.rtb_campaigns:
            return 0
        camps = self.rtb_campaigns[cpid]
        wid_daily_budget = camps.daily_website_budget
        wid_map = self.website_result.get(cpid, {})
        result = 0
        for wid, _info in wid_map.iteritems():
            key_list, _result = _info
            cost = _result.cost
            percent = cost*1.0 / wid_daily_budget
            if result == 0 or result < percent:
                result = percent
        return result

    def handle_campaign_items(self, key_list, ins_map, result_obj):
        items = super(CampaignResult, self).handle_extra_items(key_list, ins_map)
        info = "0_black"
        if len(key_list) > 0:
            cpid = int(key_list[0])
            percent = self._calculate_budget(cpid, result_obj)
            wid_percent = self._calculate_website_budget(cpid)
            percent = percent if percent > wid_percent else wid_percent
            color = self._get_budget_notice_color(percent)
            info = "%s_%s" % (percent, color)
        items.insert(1, info)
        return items

    def get_raw_data(self, filter_col=None):
        ins_map = self.find_ins_map(self._json_keys)
        result_list = []
        for _key, _info in self._result_map.items():
            key_list, _result, ts = _info
            items = _result.to_raw_items()

            items = self.handle_campaign_items(key_list, ins_map, _result) + items

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

    def load_hour_result(self, range_hours):
        cur_ts = int(time.time())
        result_map = {}
        for i in xrange(range_hours):
            ts = cur_ts - i*60*60
            cur_dt = datetime.datetime.fromtimestamp(ts)
            dt_str = cur_dt.strftime("%Y%m%d%H")
            hour_ts = self.str_hour_to_ts(dt_str)
            objs = self.get_static_data(dt_str, dt_str, 0)
            if objs:
                for cpid, obj in objs.iteritems():
                    cpid = int(cpid)
                    if cpid not in result_map:
                        result_map[cpid] = {}
                    if hour_ts not in result_map[cpid]:
                        result_map[cpid][hour_ts] = StatResult()
                    raw_obj = result_map[cpid][hour_ts]
                    tmp = StatResult()
                    tmp.from_dict(obj)
                    raw_obj.add(tmp)
        return result_map

class CampaignDateResult(BaseResult):
    def __init__(self):
        super(CampaignDateResult, self).__init__()
        self.set_items([
            'Date', 'Campaign', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'CPM', 'CTR', 'CR', 'CV', 'ROI',
            'EPM', 'EPC', 'AP', 'CPC', 'WR', 'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain', 'Orientation', 'Wid_typo',
            'Wid_digit', 'Errors', 'Bids', 'cpid'
        ])

        self.add_json_keys([{"key":"cpid", "class":Campaign, "is_rule":False}])
        self.set_tag('campaign')
        self.set_date(True)
        self.set_sort_default([["Date", 'desc']])
        self.show_items(['Date', 'Campaign', 'WR', 'Bids', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'EPM', 'CPM', 'ROI', 'CTR', 'CPC'])
        self.finish_init()

    def load_offset_result(self):
        self.load_base_offset_result()

    def static_result(self, datetime_str, k_ts, ts):
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        ret = []
        if objs:
            for cpid, obj in objs.iteritems():
                cpid = int(cpid)
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
            dt = self.ts_to_date(ts)
            datetime_str = dt.strftime('%Y-%m-%d')
            items.insert(0, datetime_str)
            items.append(cpid)
            raw_list.append(items)
        return raw_list

class CampaignHourResult(BaseResult):
    def __init__(self):
        super(CampaignHourResult, self).__init__()
        self.set_items([
            'Hour', 'Campaign', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'CPM', 'CTR', 'CR', 'CV', 'ROI',
            'EPM', 'EPC', 'AP', 'CPC', 'WR', 'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain', 'Orientation', 'Wid_typo',
            'Wid_digit', 'Errors', 'Bids', 'cpid'
        ])
        self.add_json_keys([{"key":"cpid", "class":Campaign, "is_rule":False}])
        self.set_tag('campaign')
        self.set_sort_default([["Hour", 'desc']])
        self.set_data_type(table_config.STATIC_DATA_BY_HOUR)
        self.show_items(['Hour', 'Campaign', 'WR', 'Bids', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'EPM', 'CPM', 'ROI', 'CTR', 'CPC'])
        self.finish_init()
        self._hour_data_key = ['cpid', 'views', 'cost']

    def __cal_range_day(self):
        range_days = self.get_range_days()
        days = []
        cnt = 0
        for i in xrange(range_days-1, -1, -1):
            if cnt > 1:
                break
            days.append(i)
            cnt = cnt + 1
        return days

    def get_hour_data(self, obj):
        ret = {}
        for k in self._hour_data_key:
            ret[k] = obj[k]
        return ret

    def load_result(self):
        self.set_full_day(False)

        diff_time = self.get_offset_timezone()
        start_day = self.get_start_day() + self._start_hour * ONE_HOUR_SECONDS + diff_time
        end_day = self.get_end_day() + self._end_hour * ONE_HOUR_SECONDS + diff_time

        for hour in xrange(start_day, end_day+ONE_HOUR_SECONDS, ONE_HOUR_SECONDS):
            hour_dt = datetime.datetime.fromtimestamp(hour)
            datetime_str = hour_dt.strftime('%Y%m%d%H')
            objs = self.get_static_data(datetime_str, datetime_str, hour)
            if objs:
                for cpid, obj in objs.iteritems():
                    cpid = int(cpid)
                    if cpid is not None and self.is_valid_rules({"cpid":cpid}):
                        tmp = StatResult()
                        tmp.from_dict(obj)
                        self._result_list.append((hour-diff_time, cpid, tmp))
                        self._hour_data[int(datetime_str)] = self.get_hour_data(obj)

    def get_raw_data(self, filter_col=None):
        raw_list = []
        names_map = self.get_cpnames() or self.get_db_record_names(Campaign, uid=self.get_uid())
        for ts, cpid, _result in self._result_list:
            items = _result.to_raw_items()
            cpid_name = names_map.get(cpid, "%s" % (cpid))
            items.insert(0, cpid_name)
            dt = self.ts_to_date(ts)
            datetime_str = dt.strftime('%m-%d %H:00')
            items.insert(0, datetime_str)
            items.append(cpid)
            raw_list.append(items)
        return raw_list

    def get_kendo_charts(self):
        return self.handle_hour_data()

    def get_chart_name(self, args):
        cpid = args['cpid']
        camp = global_vars.global_db_set.get_db_client().select_one(Campaign, id=int(cpid))
        return camp.name if camp else cpid

    def get_chart_title(self, args):
        return self.get_chart_name(args)

    def get_chart_sort(self, args):
        return {'field':"time", 'dir':'asc'}

    def handle_hour_data(self):
        if not self._hour_data:
            return {'charts': []}
        rules = self.get_rules()
        camp = global_vars.global_db_set.get_db_client().select_one(Campaign, id=rules['cpid'])
        cpname = camp.name if camp else str(rules['cpid'])

        time_list = sorted(self._hour_data.keys())
        time_list = time_list[-24:] if len(time_list) >= 24 else time_list
        time_dict = {}
        for t in time_list:
            time_dict[t] = self.handle_time_by_timezone(t)

        data = []
        for time_str in time_list:
            val = self._hour_data[time_str]
            data.append({"value":val['cost'], 'time':time_str, 'name':"cost"})
            data.append({"value":val['views'], 'time':time_str, 'name':"view"})

        return data

