#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import uuid

from sqlalchemy.exc import IntegrityError

import db_client as v3DB


def gen_uuid():
    return str(uuid.uuid4()).replace('-', '')


network_map = {}
source_map = {}
swap_map = {}
flow_map = {}
offer_map = {}
landpage_map = {}
path_map = {}

class DBSetting:
    def __init__(self, user, pwd, host, db_name):
        self.user = user
        self.pwd = pwd
        self.host = host
        self.db_name = db_name

v2DB = v3DB
db_setting = DBSetting('admin', '123456', 'db', 'massival')
to_db_client = v3DB.DBClient(db_setting.user, db_setting.pwd, db_setting.host, db_setting.db_name)
from_db_client = to_db_client


def copy_user(src_user, dest_user):
    dest_user.track_domains = src_user.track_domains
    dest_user.lander_domains = src_user.lander_domains
    dest_user.lander_domains_dist = src_user.lander_domains_dist
    to_db_client.do_save(dest_user)


def sync_objs(old_ins, new_ins, old_uid, new_uid):
    objs = from_db_client.select_all(old_ins, uid=old_uid)
    table_name = old_ins.__tablename__
    count = 0
    for obj in objs:
        new_obj = new_ins()
        new_obj = obj
        new_obj.id = None
        new_obj.uid = new_uid
        try:
            to_db_client.do_save(new_obj)
            count = count + 1
        except IntegrityError, ex:
            pass
    print "sync %s finished. total(%s), sync(%s)" % (table_name, len(objs), count)
    return len(objs)

def sync_landpage(old_uid, new_uid):
    objs = from_db_client.select_all(v2DB.LandingPage, uid=old_uid)
    count = 0
    for obj in objs:
        new_obj = v3DB.LandingPage(
            uid=new_uid, name=obj.name,
            page_source=obj.page_source, source=obj.source,
            hidden=obj.hidden, lander_mode=obj.lander_mode,
            lander_link=obj.lander_link
        )
        try:
            ret = to_db_client.add_one(new_obj)
            if not ret:
                raise Exception("sync landpage fail.id(%s)" % obj.id)
            landpage_map[obj.id] = new_obj.id
            count = count + 1
        except IntegrityError, ex:
            print "sync pagesource error:", obj.id, obj.uid
    print "sync pagesource finished. total(%s), sync(%s)" % (len(objs), count)

def sync_offer(old_uid, new_uid):
    objs = from_db_client.select_all(v2DB.Offer, uid=old_uid)
    count = 0
    for obj in objs:
        network_id = network_map.get(obj.network_id, None)
        if not network_id:
            raise Exception("offer not found network id: offer_id(%s), network_id(%s)" % (obj.id, obj.network_id))

        new_obj = v3DB.Offer(
                name = obj.name, url = obj.url,
                url_direct = obj.url_direct, direct_type = obj.direct_type,
                country = obj.country, payout_type = obj.payout_type,
                uid = new_uid, network_id = network_id,
                hidden = obj.hidden, direct_offer_id = obj.direct_offer_id
            )
        try:
            to_db_client.add_one(new_obj)
            count = count + 1
            offer_map[obj.id] = new_obj.id
        except IntegrityError, ex:
            print "sync offer error:", obj.id, obj.uid
    print "sync offer finished. total(%s), sync(%s)" % (len(objs), count)


def sync_campaign(old_uid, new_uid):
    objs = from_db_client.select_all(v2DB.Campaign, uid=old_uid)
    count = 0
    for obj in objs:
        source_id = source_map.get(obj.source_id, None)
        flow_id = flow_map.get(obj.flow_id, None)
        if not source_id:
            raise Exception("campaign not found traffic_source id: campaign_id(%s), source_id(%s)" % (obj.id, obj.source_id))
        if not flow_id:
            raise Exception("campaign not found flow_id: campaign_id(%s), flow_id(%s)" % (obj.id, obj.flow_id))
        old_uri = obj.uri
        uri = '/%s/%s'%(new_uid, gen_uuid())

        new_obj = v3DB.Campaign(
                name = obj.name, uri = uri, country = obj.country, cost = obj.cost,
                uid = new_uid, source_id = source_id, flow_id = flow_id,
                ck_cloak = obj.ck_cloak, ck_cloak_html = obj.ck_cloak_html,
                ck_cloak_ts = obj.ck_cloak_ts, ck_cloak_ts_html = obj.ck_cloak_ts_html,
                ck_android = obj.ck_android, ck_android_html = obj.ck_android_html,
                ck_websiteid_digit = obj.ck_websiteid_digit, ck_websiteid_typo = obj.ck_websiteid_typo,
                ck_websiteid_html = obj.ck_websiteid_html,
                ck_meta_refresh=obj.ck_meta_refresh, lander_domains_dist=obj.lander_domains_dist,
                track_domain=obj.track_domain, hidden=obj.hidden
            )
        try:
            to_db_client.do_save(new_obj)
            count = count + 1
        except IntegrityError, ex:
            print "sync campaign error:", obj.id, obj.uid
    print "sync campaign finished. total(%s), sync(%s)" % (len(objs), count)
    return len(objs)

def sync_trafficsource(old_uid, new_uid):
    objs = from_db_client.select_all(v2DB.TrafficSource, uid=old_uid)
    tb_name = v3DB.TrafficSource.__tablename__
    count = 0
    for obj in objs:
        postback_url = obj.postback_url
        if not postback_url or postback_url == '0':
            postback_url = ''

        ad_server_domains = obj.ad_server_domains
        if not ad_server_domains or ad_server_domains == '0':
            ad_server_domains = ''

        new_obj = v3DB.TrafficSource(
                name = obj.name, postback_url = postback_url,
                fields = obj.fields, timezone = obj.timezone,
                ad_server_domains = ad_server_domains,
                uid = new_uid
            )
        try:
            to_db_client.add_one(new_obj)
            count = count + 1
            source_map[obj.id] = new_obj.id
        except IntegrityError, ex:
            print "sync traffic_source error:", obj.id, obj.uid
    print "sync %s finished. total(%s), sync(%s)" % (tb_name, len(objs), count)

def sync_affiliatenetwork(old_uid, new_uid):
    objs = from_db_client.select_all(v2DB.AffiliateNetwork, uid=old_uid)
    tb_name = v3DB.AffiliateNetwork.__tablename__
    count = 0
    for obj in objs:
        new_obj = v3DB.AffiliateNetwork(
                name = obj.name, uid = new_uid,
            )
        try:
            to_db_client.add_one(new_obj)
            count = count + 1
            network_map[obj.id] = new_obj.id
        except IntegrityError, ex:
            print "sync error:", obj.id, obj.uid
    print "sync %s finished. total(%s), sync(%s)" % (tb_name, len(objs), count)

def sync_path(old_uid, new_uid):
    objs = from_db_client.select_all(v2DB.Path, uid=old_uid)
    tb_name = v3DB.Path.__tablename__
    count = 0
    for obj in objs:
        offer_list = obj.offers.split(',')
        new_list = []
        for o in offer_list:
            k = offer_map.get(int(o), None)
            if k is None:
                raise Exception("path not found offer id. path_id(%s), offer_id(%s)" % (obj.id, o))
            new_list.append(str(k))
        list_str = ','.join(new_list) if new_list else ""

        landpage_list = obj.landing_pages.split(',')
        new_list = []
        for l in landpage_list:
            l = l.split(';')[0]
            k = landpage_map.get(int(l), None)
            if k is None:
                raise Exception("landing page not found: %d", int(l))

            new_list.append('%s;0'%k)
        landpage_str = ','.join(new_list) if new_list else ""

        new_obj = v3DB.Path(
                name = obj.name, direct_linking = obj.direct_linking,
                landing_pages = landpage_str, offers = list_str,
                uid = new_uid
            )
        try:
            to_db_client.add_one(new_obj)
            path_map[obj.id] = new_obj.id
            count = count + 1
        except IntegrityError, ex:
            print "sync error:", obj.id, obj.uid
    print "sync %s finished. total(%s), sync(%s)" % (tb_name, len(objs), count)

def sync_swaprotation(old_uid, new_uid):
    objs = from_db_client.select_all(v2DB.SwapRotation, uid=old_uid)
    tb_name = v3DB.SwapRotation.__tablename__
    count = 0
    for obj in objs:
        path_list= obj.paths.split(',')
        new_list = []
        for p in path_list:
            p, power = p.split(';')
            k = path_map.get(int(p), None)
            if k is None:
                raise Exception("swaprotation not found path id. swap_id(%s), path_id(%s)" % (obj.id, p))

            new_list.append('%s;%s'%(k, int(power)))
        path_str = ','.join(new_list) if new_list else ""
        new_obj = v3DB.SwapRotation(
                name = obj.name, paths = path_str,
                uid = new_uid, rules = "",
            )
        try:
            to_db_client.add_one(new_obj)
            count = count + 1
            swap_map[obj.id] = new_obj.id
        except IntegrityError, ex:
            print "sync error:", obj.id, obj.uid
            continue

    print "sync %s finished. total(%s), sync(%s)" % (tb_name, len(objs), count)


def sync_flow(old_uid, new_uid):
    objs = from_db_client.select_all(v2DB.Flow, uid=old_uid)
    tb_name = v3DB.Flow.__tablename__
    count = 0
    for obj in objs:
        swap_list = obj.swaps.split(',')
        new_list = []
        for p in swap_list:
            k = swap_map.get(int(p), None)
            if k is None:
                raise Exception("flow not found path id. flow(%s), swap_id(%s)" % (obj.id, p))

            new_list.append('%s'%(k))
        swap_str = ','.join(new_list) if new_list else ""
        new_obj = v3DB.Flow(
                name = obj.name, swaps = swap_str,
                uid = new_uid
            )
        try:
            to_db_client.add_one(new_obj)
            count = count + 1
            flow_map[obj.id] = new_obj.id
        except IntegrityError, ex:
            print "sync error:", obj.id, obj.uid
            continue

    print "sync %s finished. total(%s), sync(%s)" % (tb_name, len(objs), count)



def sync_db(old_uid, new_uid):
    src_user = to_db_client.select_one(v3DB.User, id=old_uid)
    dest_user = to_db_client.select_one(v3DB.User, id=new_uid)

    copy_user(src_user, dest_user)
    sync_trafficsource(old_uid, new_uid)
    sync_affiliatenetwork(old_uid, new_uid)
    sync_offer(old_uid, new_uid)
    sync_landpage(old_uid, new_uid)
    sync_path(old_uid, new_uid)
    sync_swaprotation(old_uid, new_uid)
    sync_flow(old_uid, new_uid)
    sync_campaign(old_uid, new_uid)
    print "sync db is all finished."

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "python sydb.py old_uid new_uid"
        exit(-1)
    old_uid = int(sys.argv[1])
    new_uid = int(sys.argv[2])
    sync_db(old_uid, new_uid)

