#!/usr/bin/env python
# -*- coding:utf-8 -*-

import init_env
from adminsvr.db_client import AdminOffer, Offer
from adminsvr.global_vars import global_db_set as DBSet
from adminsvr.utils import decode_from_utf8, encode_from_utf8
from adminsvr.static_result import str_hour_to_ts
from os import path as osp

def update_offer_intro():
    offers = DBSet.get_db_client().select_all(AdminOffer)
    for o in offers:
        if o.introduction == "":
            continue
        objs = DBSet.get_db_client().select_all(Offer, direct_offer_id=o.id)
        intro = o.introduction
        for obj in objs:
            obj.introduction = intro
            if DBSet.get_db_client().do_save(obj):
                print obj.uid, obj.id, obj.name


#check postback
class CheckPostback(object):
    def __init__(self, cpid, start_str, file_path):
        self.cpid = cpid
        self.start_str = start_str
        self.start_ts = str_hour_to_ts
        self.file_path = file_path

    def load_rids(self):
        self.rids_map = {}
        path = osp.join(self.file_path, "rids.txt")
        try:
            with open(path, "r") as f:
                for line in f:
                    tmp = line.split(",")
                    rid = tmp[0]
                    self.rids_map[rid] = 1
        except Exception, ex:
            print ex

    def load_cids(self):
        self.cids_map = {}
        filename = "cids.txt" 
        path = osp.join(self.file_path, filename)
        try:
            with open(path, "r") as f:
                for line in f:
                    tmp = line.split(",")
                    rid = tmp[0]
                    cid = tmp[1]
                    self.cids_map[cid] = rid
        except Exception, ex:
            print ex

    def load_postback(self):
        self.postback_map = {}
        filename = "pbs.txt" 
        path = osp.join(self.file_path, filename)
        try:
            with open(path, "r") as f:
                for line in f:
                    tmp = line.split(",")
                    cid = tmp[0]
                    if cid in self.cids_map:
                        rid = self.cids_map[cid]
                        if rid in self.self.rids_map:
                            self.postback_map[cid] = rid
        except Exception, ex:
            print ex

    def write_result(self):
        for cid, rid in self.postback_map.iteritems():
            print rid, cid

    def check(self):
        self.load_rids()
        self.load_cids()
        self.load_postback()
        self.write_result()

def check_postback(cpid, start_str, path):
    ins = CheckPostback(cpid, start_str, path)
    ins.check()

if __name__ == '__main__':
    DBSet.set_init(True)
    check_postback(4050, "2016071822", "check_pb")

