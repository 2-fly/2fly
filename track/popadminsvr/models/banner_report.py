#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime

from report import BaseResult
from db_client import Campaign
from stat_result import StatResult
from config import table_config
from utils import ONE_DAY_SECONDS
from commlib.utils.utils import ONE_HOUR_SECONDS
import global_vars

class BannerResult(BaseResult):
    def __init__(self):
        super(BannerResult, self).__init__()
        self.set_items([
            'Campaign', 'ImageUrl', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'CPM', 'CTR', 'CR', 'CV', 'ROI',
            'EPM', 'EPC', 'AP', 'CPC', 'WR', 'Warns', 'Cloak_ts', 'Cloak', 'Track_domain', 'Lander_domain', 'Orientation', 'Wid_typo',
            'Wid_digit', 'Errors', 'Bid', 'bannerid', 'cpid',
        ])

        def banner_handler(**kwargs):
            banner = kwargs['id']
            camp = kwargs['ins']
            if camp.image_urls:
                urls = camp.image_urls.split(",")
                banner = int(banner) - 1
                if len(urls) < banner:
                    return str(banner + 1)
                else:
                    return urls[banner].split("/")[-1]
            else:
                return banner

        self.add_json_keys([
            {"key":"cpid", "class":Campaign, "is_rule":False},
            {"key":"banner", 'class':Campaign, 'handler':banner_handler, "is_rule":False},
        ])
        self.set_tag('tok1')
        self.set_sort_default([["Views", 'desc']])
        self.show_items(['Campaign', 'ImageUrl', 'WR', 'Views', 'Visits', 'Clicks', 'Convs', 'Profit', 'Revenue', 'Cost', 'EPM', 'CPM', 'ROI', 'CTR', 'CPC'])
        self.add_filter_items('ImageUrl', 'contains')
        self.finish_init()

    def handle_extra_items(self, key_list, ins_map):
        cpid, banner_id = key_list
        camp = ins_map['cpid'].get(int(cpid), None)
        banner = int(banner_id) if banner_id.isdigit() else "Unknow"
        cpname = cpid
        if camp:
            cpname = camp.name
            if camp.image_urls and type(banner) == int:
                urls = [url for url in camp.image_urls.split(",")]
                if len(urls) >= banner:
                    banner = urls[banner - 1]
        return [cpname, banner]

    def static_result(self, datetime_str, k_ts, ts):
        json_keys = self._json_keys
        objs = self.get_static_data(datetime_str, datetime_str, k_ts)
        if objs:
            for cpid, obj in objs.iteritems():
                for banner_id, bn_obj in obj.iteritems():
                    bn_obj.update({'cpid':cpid, 'bannerid':banner_id})
                    if not self.is_valid_rules({"cpid":int(cpid)}):
                        continue

                    if self._is_show_date:
                        keys = ts
                    else:
                        keys = banner_id
                    if keys not in self._result_map:
                        tmp = StatResult()
                        self._result_map[keys] = ([cpid, banner_id], tmp, ts)
                    self._result_map[keys][1].add_raw(bn_obj)

    def get_bottom_static(self):
        result = {
                "Campaign":"Total", "ImageUrl":""
        }
        return result



