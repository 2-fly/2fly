#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime

from report import BaseResult
from db_client import Campaign
from stat_result import StatResult
from config import table_config, country_config
from utils import ONE_DAY_SECONDS
from commlib.utils.utils import ONE_HOUR_SECONDS
import global_vars

def get_bottom(self):
    result_list = []
    total = StatResult()
    for keys, _info in self._result_map.items():
        key_list, _result, _ts  = _info
        total.add(_result)
    items = total.to_raw_items()
    items.insert(0, "")
    items.insert(0, "Total")
    items.append(-1)
    tmp = {}
    for i in xrange(len(items)):
        tmp[self._items[i]] = items[i]
    result_list.append(tmp)
    return result_list



class OsResult(BaseResult):
    def __init__(self):
        super(OsResult, self).__init__()
        self.set_items([
            'Campaign', 'OS', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'CPM', 'CTR', 'CR', 'CV', 'ROI',
            'EPM', 'EPC', 'AP', 'CPC', 'WR', 'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain', 'Orientation', 'Wid_typo',
            'Wid_digit', 'Errors', 'Bid', 'os', 'cpid',
        ])

        self.add_json_keys([
            {"key":"cpid", "class":Campaign, "is_rule":False},
            {"key":"os", 'class':Campaign, "is_rule":False},
        ])
        self.set_tag('os')
        self.set_sort_default([["Views", 'desc']])
        self.add_dashboard_head(['Campaign'])
        self.show_items(['Campaign', 'OS',  'WR', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'EPM', 'CPM', 'ROI', 'CTR', 'CPC'])
        self.add_filter_items('OS', 'contains')
        self.finish_init()

    def handle_extra_items(self, key_list, ins_map):
        cpid, os = key_list
        camp = ins_map['cpid'].get(int(cpid), None)
        cpname = camp.name if camp else int(cpid)
        return [cpname, os]

    def static_result(self, datetime_str, k_ts, ts):
        json_keys = self._json_keys
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for cpid, obj in objs.iteritems():
                for os, bn_obj in obj.iteritems():
                    bn_obj.update({'cpid':cpid, 'os':os})
                    if not self.is_valid_rules({"cpid":int(cpid)}):
                        continue

                    if self._is_show_date:
                        keys = ts
                    else:
                        keys = os
                    if keys not in self._result_map:
                        tmp = StatResult()
                        self._result_map[keys] = ([cpid, os], tmp, ts)
                    self._result_map[keys][1].add_raw(bn_obj)

    def get_bottom_static(self):
        ret = {
            "Campaign":"Total", "OS":""
        }
        return ret

class BrowserResult(BaseResult):
    def __init__(self):
        super(BrowserResult, self).__init__()
        self.set_items([
            'Campaign', 'Browser', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'CPM', 'CTR', 'CR', 'CV', 'ROI',
            'EPM', 'EPC', 'AP', 'CPC', 'WR', 'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain', 'Orientation', 'Wid_typo',
            'Wid_digit', 'Errors', 'Bid', 'browser', 'cpid',
        ])
        self.add_json_keys([
            {"key":"cpid", "class":Campaign, "is_rule":False},
            {"key":"os", 'class':Campaign, "is_rule":False},
        ])

        self.set_tag('browser')
        self.set_sort_default([["Views", 'desc']])
        self.add_dashboard_head(['Campaign'])
        self.show_items(['Campaign', 'Browser', 'WR', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'EPM', 'CPM', 'ROI', 'CTR', 'CPC'])
        self.add_filter_items('Browser', 'contains')
        self.finish_init()

    def handle_extra_items(self, key_list, ins_map):
        cpid, browser = key_list
        camp = ins_map['cpid'].get(int(cpid), None)
        cpname = camp.name if camp else int(cpid)
        return [cpname, browser]

    def static_result(self, datetime_str, k_ts, ts):
        json_keys = self._json_keys
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for cpid, obj in objs.iteritems():
                for browser, bn_obj in obj.iteritems():
                    bn_obj.update({'cpid':cpid, 'browser':browser})
                    if not self.is_valid_rules({"cpid":int(cpid)}):
                        continue

                    if self._is_show_date:
                        keys = ts
                    else:
                        keys = browser
                    if keys not in self._result_map:
                        tmp = StatResult()
                        self._result_map[keys] = ([cpid, browser], tmp, ts)
                    self._result_map[keys][1].add_raw(bn_obj)

    def get_bottom_static(self):
        return {"Campaign":"Total", "Browser":""}

class CountryResult(BaseResult):
    def __init__(self):
        super(CountryResult, self).__init__()
        self.set_items([
            'Campaign', 'Country', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'CPM', 'CTR', 'CR', 'CV', 'ROI',
            'EPM', 'EPC', 'AP', 'CPC', 'WR', 'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain', 'Orientation', 'Wid_typo',
            'Wid_digit', 'Errors', 'Bid', 'country', 'cpid',
        ])
        self.add_json_keys([
            {"key":"cpid", "class":Campaign, "is_rule":False},
            {"key":"os", 'class':Campaign, "is_rule":False},
        ])

        self.set_tag('country')
        self.set_sort_default([["Views", 'desc']])
        self.add_dashboard_head(['Campaign'])
        self.show_items(['Campaign', 'Country', 'WR', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'EPM', 'CPM', 'ROI', 'CTR', 'CPC'])
        self.add_filter_items('Country', 'contains')
        self.finish_init()

    def handle_extra_items(self, key_list, ins_map):
        cpid, country = key_list
        camp = ins_map['cpid'].get(int(cpid), None)
        cpname = camp.name if camp else int(cpid)
        return [cpname, country]

    def static_result(self, datetime_str, k_ts, ts):
        json_keys = self._json_keys
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for cpid, obj in objs.iteritems():
                for country, bn_obj in obj.iteritems():
                    bn_obj.update({'cpid':cpid, 'country':country})
                    if not self.is_valid_rules({"cpid":int(cpid)}):
                        continue

                    if self._is_show_date:
                        keys = ts
                    else:
                        keys = country
                    if keys not in self._result_map:
                        tmp = StatResult()
                        self._result_map[keys] = ([cpid, country], tmp, ts)
                    self._result_map[keys][1].add_raw(bn_obj)

    def get_bottom_static(self):
        return {"Campaign":"Total", "Country":""}
