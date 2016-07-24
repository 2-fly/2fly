#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime, time
import ujson

from report import BaseResult
from db_client import Campaign
from stat_result import StatResult
from config import table_config
from utils import ONE_DAY_SECONDS
from commlib.utils.utils import ONE_HOUR_SECONDS
from global_vars import tmpl_reader, global_db_set as DBSet
import global_vars

class WebsiteResult(BaseResult):
    def __init__(self):
        super(WebsiteResult, self).__init__()
        self._args['has_include'] = True
        self.set_items([
            'Campaign', 'Website', 'BudgetRate', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'CPM', 'CTR', 'CR', 'CV', 'ROI',
            'EPM', 'EPC', 'AP', 'CPC', 'WR', 'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain', 'Orientation', 'Wid_typo',
            'Wid_digit', 'Errors', "Bids", 'cpid', 'website', "clude", "Bid",  "Budget"
        ])

        self.add_json_keys([
            {"key":"cpid", "class":Campaign, "is_rule":False},
            {"key":"website", "is_rule":False},
        ])
        self.set_tag('website')
        self.set_sort_default([["Views", 'desc']])
        self.show_items([{"type":"checkbox", "field":""}, 'Campaign', 'Website', 'BudgetRate', 'WR', "Bids", 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'EPM', 'CPM', 'ROI', 'CTR', 'CPC', {"field":"Bid", 'edit':True}, {"field":"Budget", 'edit':True}, {'is_key':True,"field":"clude", "hidden":True}])
        self.add_filter_items('Website', 'contains')
        self.add_dashboard_head(['Campaign'])
        self.finish_init()

    def get_edit(self):
        return True

    def init_data(self):
        self._init_rtb_campaign(self.get_uid())

    def _init_rtb_campaign(self, uid):
        self.rtb_campaigns = {}
        camps = DBSet.get_db_client().select_all(Campaign, uid=uid)
        for o in camps:
            self.rtb_campaigns[o.id] = o

        self.rtb_website = {}
        for o in camps:
            if not o.website_info_list:
                continue
            self.rtb_website.setdefault(o.id, {})
            tmp = o.website_info_list.split(",")
            for w in tmp:
                info = w.split(";")
                self.rtb_website[o.id][info[0]] = info

    def static_result(self, datetime_str, k_ts, _):
        json_keys = self._json_keys
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for cpid, obj in objs.iteritems():
                for website_id, ws_obj in obj.iteritems():
                    ws_obj.update({'cpid':cpid, 'website':website_id})
                    if not self.is_valid_rules({"cpid":int(cpid)}):
                        continue

                    cpid = int(cpid)
                    keys = website_id
                    self._result_map.setdefault(cpid, {})
                    if keys not in self._result_map[cpid]:
                        tmp = StatResult()
                        self._result_map[cpid][keys] = ([cpid, website_id], tmp)
                    self._result_map[cpid][keys][1].add_raw(ws_obj)

    def get_bottom_static(self):
        result = {
                "":"", "Campaign":"Total", "Website":"", "BudgetRate":"", "Budget":"", "Bid":""
        }
        return result

    def get_filter_condition(self, args):
        ret = []
        for k, v in args.items():
            if k.startswith("max"):
                k = k[4:]
                if k not in self._items:
                    continue
                v = float(v)
                index = self._items.index(k)
                ret.append({'indx':index, "field":"max", "val":v})
            elif k.startswith("min"):
                k = k[4:]
                if k not in self._items:
                    continue
                v = float(v)
                index = self._items.index(k)
                ret.append({'indx':index, "field":"min", "val":v})
        return ret

    def get_kendo_async_data(self, args):
        hours = int(args.get("hours", 0))
        if hours:
            return self.load_hour_result(hours, args)
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

    def filter_item(self, filter_cdts, item):
        for f in filter_cdts:
            v = item[f['indx']]
            if f['field'] == "max":
                if v > f['val']:
                    return False
            if f['field'] == "min":
                if v < f['val']:
                    return False
        return True

    def _calculete_budget(self, cpid, wid, result_obj):
        if cpid not in self.rtb_campaigns:
            return 0
        cost = result_obj.cost
        if cpid in self.rtb_website and wid in self.rtb_website[cpid]:
            wid_budget = float(self.rtb_website[cpid][wid][2])
            if wid_budget == -1:
                wid_budget = self.rtb_campaigns[cpid].daily_website_budget
        else:
            wid_budget = self.rtb_campaigns[cpid].daily_website_budget
        percent = cost*1.0 / wid_budget
        return percent

    def handle_website_items(self, key_list, ins_map, result_obj):
        items = super(WebsiteResult, self).handle_extra_items(key_list, ins_map)
        if len(key_list) > 1:
            cpid = int(key_list[0])
            wid = key_list[1]
            percent = self._calculete_budget(cpid, wid, result_obj)
            items.insert(2, percent)
        return items

    def get_args(self, uid, args):
        cpid = int(args['cpid'])
        camp = DBSet.get_db_client().select_one(Campaign, id=cpid, uid=uid)
        return {'has_include':True if camp.include_websites else False}

    def get_raw_data(self, filter_col=None):
        ins_map = self.find_ins_map(self._json_keys)
        cpid = self._rules['cpid']
        camp = ins_map['cpid'][cpid]
        exclude = camp.exclude_websites.split(",")
        include = [e for e in camp.include_websites.split(",") if e]
        wb_budget_list = camp.website_info_list.split(",") if camp and camp.website_info_list else []
        wb_info_map = {}
        for e in wb_budget_list:
            info = e.split(";")
            wb_info_map[info[0]] = info
        if not include:
            self._args['has_include'] = False
        result_list = []
        for _cpid, detail in self._result_map.items():
            if cpid != int(_cpid):
                continue
            for _key, _info in detail.items():
                key_list, _result = _info
                items = _result.to_raw_items()
                items = self.handle_website_items(key_list, ins_map, _result) + items

                is_continue = False
                for i in xrange(len(key_list)):
                    if self._json_keys[i].get("add_ignore", None):
                        continue
                    k = key_list[i]
                    items.append(k)
                    if self._json_keys[i]['key'] == "website":
                        if include and k in include:
                            items.append(1)
                        elif exclude and k in exclude:
                            items.append(0)
                        else:
                            items.append(-1)

                if filter_col:
                    if not self.filter_item(filter_col, items):
                        continue
                bid = "auto"
                budget = "unlimited"
                if key_list[1] in wb_info_map:
                    info = wb_info_map[key_list[1]]
                    if len(info) >= 3:
                        bid = float(info[1]) if info[1] != "-1" else "auto"
                        budget = float(info[2]) if info[2] != "-1" else "unlimited"
                items.append(bid)
                items.append(budget)

                result_list.append(items)
        return result_list

    def get_toolbar(self):
        return "custom"

    def load_hour_result(self, range_hours, args):
        self.set_full_day(False)
        cur_ts = int(time.time())
        for i in xrange(range_hours):
            ts = cur_ts - i*60*60
            cur_dt = datetime.datetime.fromtimestamp(ts)
            dt_str = cur_dt.strftime("%Y%m%d%H")
            hour_ts = self.str_hour_to_ts(dt_str)
            self.static_result(dt_str, hour_ts, 0)
        filter_cdt = self.get_filter_condition(args)
        raw_data = self.get_raw_data(filter_cdt)
        result = []
        for d in raw_data:
            tmp = {}
            for i in xrange(len(d)):
                item = self._items[i]
                item = item['name'] if type(item) == dict else item
                tmp[item] = d[i]
            result.append(tmp)
            if self.is_length_limit(result):
                break
        return result
