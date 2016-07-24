#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import sys
import traceback
import os
from os import path as osp

from termcolor import colored

import init_env

from commlib.utils.template_pool import TemplatePool
from adminsvr.db_client import *
import adminsvr.settings as settings

template_pool = TemplatePool()

# 建立database连接
db_client = DBClient(settings.db_user, settings.db_password,
        settings.db_host, settings.db_name)




class CheckerInfo(object):
    def __init__(self):
        self.lpid = -1
        self.cpid = -1
        self.name = ''
        self.page_source = ''



class LanderAsset(object):
    def __init__(self):
        self.lpid = -1
        self.cpid = -1
        self.name = ''
        self.url = ''
        self.key = ''
        self.file_name = ''
        self.real_path = ''



class CampaignHtml(object):
    def __init__(self):
        self.cpid = -1
        self.name = ''
        self.real_path = ''
        self.html = ''



class CampaignChecker(object):
    def __init__(self):
        self.missing_campaign_htmls = {}
        self.missing_lander_htmls = {}
        self.missing_lander_assets = {}
        self.invalid_lander_vars = {}


    def log_error(self, s):
        print colored(s, 'red')


    def read_content_from_uid(self, uid, file_name):
        path = osp.join(settings.static_root_dir, str(uid), file_name)
        with open(path, 'r') as f:
            return f.read()


    def check_exist_from_uid(self, uid, file_name):
        path = self.get_realpath_from_uid(uid, file_name)
        return os.access(path, os.R_OK)

    def get_realpath_from_uid(self, uid, file_name):
        path = osp.join(settings.static_root_dir, str(uid), file_name)
        return path


    def check_path(self, uid, cpid, path):
        try:
            landing_page_ids = [int(i) for i in path.landing_pages.split(',')]
        except ValueError:
            raise ValueError('landing_page_ids error: %s'%path.landing_pages)

        if len(landing_page_ids) < 1:
            raise Exception('no landing page ids found')

        try:
            offer_ids = [int(i) for i in path.offers.split(',')]
        except ValueError:
            raise ValueError('offer_ids error: %s'%path.offers)

        if len(offer_ids) < 1:
            raise Exception('no offer ids found')

        rid = 'rid_xxx'
        session_info = {}

        landing_pages = []
        for landing_page_id in landing_page_ids:
            landing_page = db_client.select_one(LandingPage, id=landing_page_id)
            if not landing_page or landing_page.uid != uid:
                raise Exception('landing page not found: %d'%landing_page_id)

            landing_pages.append(landing_page)

        offers = []
        for offer_id in offer_ids:
            offer = db_client.select_one(Offer, id=offer_id)
            if not offer or offer.uid != uid:
                raise Exception('offer not found: %d'%offer_id)

            offers.append(offer)


        for landing_page in landing_pages:
            tmpl_path = self.get_realpath_from_uid(uid, landing_page.page_source)
            if not os.access(tmpl_path, os.R_OK):
                info = LanderAsset()
                info.lpid = landing_page.id
                info.name = landing_page.name
                info.url = ''
                info.key = ''
                info.file_name = landing_page.page_source
                info.real_path = tmpl_path
                self.missing_lander_htmls.setdefault(landing_page.id, {})
                self.missing_lander_htmls[landing_page.id][tmpl_path] = info
                continue

            page_str = self.render_page1(tmpl_path, uid, session_info, rid,
                    offers, landing_pages, landing_page.id, landing_page, cpid)



    def check_uid(self, uid):
        campaigns = db_client.select_all(Campaign)
        for campaign in campaigns:
            if campaign.uid != uid:
                continue

            try:
                self.check_campaign(uid, campaign.id)
            except Exception, ex:
                #self.log_error(str(ex))
                print traceback.format_exc()

        print ''
        print '-'*40, 'missing_campaign_htmls'
        for k, v in self.missing_campaign_htmls.iteritems():
            for _path, _info in v.iteritems():
                cpname = ''
                if _info.cpid != -1:
                    campaign = db_client.select_one(Campaign, id=_info.cpid)
                    if campaign and campaign.uid == uid:
                        cpname = campaign.name
                self.log_error('%s\t\t%s\t\tcampaign[%s] campaign[%s]'%(_info.html, _info.real_path, _info.name, cpname))

        print ''
        print '-'*40, 'missing_lander_htmls'
        for k, v in self.missing_lander_htmls.iteritems():
            for _path, _info in v.iteritems():
                cpname = ''
                if _info.cpid != -1:
                    campaign = db_client.select_one(Campaign, id=_info.cpid)
                    if campaign and campaign.uid == uid:
                        cpname = campaign.name
                self.log_error('%s\t\t%s\t\tlander[%s] campaign[%s]'%(_info.file_name, _info.real_path, _info.name, cpname))

        print ''
        print '-'*40, 'missing_lander_assets'
        for k, v in self.missing_lander_assets.iteritems():
            for _path, _info in v.iteritems():
                cpname = ''
                if _info.cpid != -1:
                    campaign = db_client.select_one(Campaign, id=_info.cpid)
                    if campaign and campaign.uid == uid:
                        cpname = campaign.name
                self.log_error('%s\t\t%s\t\tlander[%s] campaign[%s]'%(_info.url, _info.real_path, _info.name, cpname))

        print ''
        print '-'*40, 'invalid_lander_vars'
        for k, v in self.invalid_lander_vars.iteritems():
            for _path, _info in v.iteritems():
                cpname = ''
                if _info.cpid != -1:
                    campaign = db_client.select_one(Campaign, id=_info.cpid)
                    if campaign and campaign.uid == uid:
                        cpname = campaign.name
                self.log_error('%s\t\t%s\t\tlander[%s] campaign[%s]'%(_info.page_source, _path, _info.name, cpname))


    def check_campaign(self, uid, cpid):
        campaign = db_client.select_one(Campaign, id=cpid)
        if not campaign or campaign.uid != uid:
            raise Exception('campaign not found: %d'%cpid)


        if campaign.ck_cloak_ts == 1 \
                and campaign.ck_cloak_ts_html != '' \
                and campaign.ck_cloak_ts_html != '0':
            if not self.check_exist_from_uid(uid, campaign.ck_cloak_ts_html):
                info = CampaignHtml()
                info.cpid = campaign.id
                info.name = campaign.name
                info.real_path = self.get_realpath_from_uid(uid, campaign.ck_cloak_ts_html)
                info.html = campaign.ck_cloak_ts_html
                self.missing_campaign_htmls.setdefault(campaign.id, {})
                self.missing_campaign_htmls[campaign.id][campaign.ck_cloak_ts_html] = info


        if campaign.ck_android == 1 and campaign.ck_android_html != '' and \
                campaign.ck_android_html != '0':
            if not self.check_exist_from_uid(uid, campaign.ck_android_html):
                info = CampaignHtml()
                info.cpid = campaign.id
                info.name = campaign.name
                info.real_path = self.get_realpath_from_uid(uid, campaign.ck_android_html)
                info.html = campaign.ck_android_html
                self.missing_campaign_htmls.setdefault(campaign.id, {})
                self.missing_campaign_htmls[campaign.id][campaign.ck_android_html] = info


        if campaign.ck_websiteid_digit == 1 or campaign.ck_websiteid_typo == 1:
            if not self.check_exist_from_uid(uid, campaign.ck_websiteid_html):
                info = CampaignHtml()
                info.cpid = campaign.id
                info.name = campaign.name
                info.real_path = self.get_realpath_from_uid(uid, campaign.ck_websiteid_html)
                info.html = campaign.ck_websiteid_html
                self.missing_campaign_htmls.setdefault(campaign.id, {})
                self.missing_campaign_htmls[campaign.id][campaign.ck_websiteid_html] = info


        if campaign.ck_cloak == 1 \
                and campaign.ck_cloak_html != '' \
                and campaign.ck_cloak_html != '0':
            if not self.check_exist_from_uid(uid, campaign.ck_cloak_html):
                info = CampaignHtml()
                info.cpid = campaign.id
                info.name = campaign.name
                info.real_path = self.get_realpath_from_uid(uid, campaign.ck_cloak_html)
                info.html = campaign.ck_cloak_html
                self.missing_campaign_htmls.setdefault(campaign.id, {})
                self.missing_campaign_htmls[campaign.id][campaign.ck_cloak_html] = info


        swap = db_client.select_one(SwapRotation, id=campaign.swap_id)
        if not swap or swap.uid != uid:
            raise Exception('swap_rotation not found: %d'%campaign.swap_id)

        path_ids = swap.paths.split(',')
        try:
            path_ids = [int(path_id.strip()) for path_id in path_ids]
        except ValueError:
            raise ValueError('path_ids errors: %s'%swap.paths)

        if len(path_ids) < 1:
            raise Exception('no path ids found')

        for path_id in path_ids:
            path = db_client.select_one(Path, id=path_id)
            if not path or path.uid != uid:
                raise Exception('path not found: %d'%path_id)

            self.check_path(uid, cpid, path)




    def check_pagesource_urls(self, html_source, uid, cur_landing_page, cpid):
        static_dir = osp.join(settings.static_root_dir, str(uid))
        cur_dir = osp.join(settings.static_root_dir, str(uid), osp.dirname(cur_landing_page.page_source))
        dir_keys = [
            ('static_dir', static_dir),
            ('cur_dir', cur_dir)
        ]

        for _key, _path in dir_keys:
            _key = '${%s}/'%_key
            start_pos = 0
            while 1:
                # no more _key found
                pos = html_source.find(_key, start_pos)
                if pos == -1:
                    break

                next_pos = pos + len(_key)
                end_set = ['"', "'", ' ', ')', '${']
                end_pos = 1024*1024*1024
                end_str = None

                for _stop in end_set:
                    tmp_pos = html_source.find(_stop, next_pos)
                    if tmp_pos != -1 and tmp_pos < end_pos:
                        end_pos = tmp_pos
                        end_str = _stop

                if end_str is not None:
                    if end_str == '${':
                        start_pos = end_pos
                        # don't check url
                        continue
                    else:
                        start_pos = end_pos + 1
                        url = html_source[pos:end_pos]
                        real_path = url.replace(_key[:-1], _path)
                        if not os.access(real_path, os.R_OK):
                            info = LanderAsset()
                            info.lpid = cur_landing_page.id
                            info.cpid = cpid
                            info.name = cur_landing_page.name
                            info.url = url
                            info.key = _key[:-1]
                            info.file_name = cur_landing_page.page_source
                            info.real_path = real_path
                            self.missing_lander_assets.setdefault(cur_landing_page.id, {})
                            self.missing_lander_assets[cur_landing_page.id][real_path] = info
                else:
                    # to end
                    real_path = url.replace(_key[:-1], _path)
                    if not os.access(real_path, os.R_OK):
                        info = LanderAsset()
                        info.lpid = cur_landing_page.id
                        info.cpid = cpid
                        info.name = cur_landing_page.name
                        info.url = url
                        info.key = _key[:-1]
                        info.file_name = cur_landing_page.page_source
                        info.real_path = real_path
                        self.missing_lander_assets.setdefault(cur_landing_page.id, {})
                        self.missing_lander_assets[cur_landing_page.id][real_path] = info
                    break



    def check_pagesource_envs(self, html_source, infos, lander, cpid):
        pattern = re.compile(r'\${.*?}')
        all_envs = pattern.findall(html_source)
        for _env in all_envs:
            env = _env[2:-1]
            if env not in infos:
                #self.log_error('lander "%s" \'s env is not valid: %s'%(lander.name, _env))
                info = CheckerInfo()
                info.lpid = lander.id
                info.cpid = cpid
                info.name = lander.name
                info.page_source = lander.page_source
                self.invalid_lander_vars.setdefault(lander.id, {})
                self.invalid_lander_vars[lander.id][_env] = info
                continue

            value = infos[env]

        #pattern = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


    def render_page1(self, tmpl_path, uid, session_info, rid,
            offers, landing_pages, cur_lpid, cur_landing_page, cpid):

        d = {}
        d['uid'] = uid
        d['rid'] = rid
        d['static_dir'] = '%s/%d'%(settings.static_html_dir, uid)
        d['cur_dir'] = osp.join(settings.static_html_dir, str(uid), osp.dirname(cur_landing_page.page_source))

        d['deviceid'] = session_info.get('_did', '')
        d['brand'] = session_info.get('_brand', '')
        d['model'] = session_info.get('_model', '')
        d['browser'] = session_info.get('_browser', '')
        d['browser_ver'] = session_info.get('_browser_ver', '')
        d['os'] = session_info.get('_os', '')
        d['os_ver'] = session_info.get('_os_ver', '')
        d['country'] = session_info.get('_country', '')
        d['country_name'] = session_info.get('_country_name', '')
        d['city'] = session_info.get('_city', '')
        d['isp'] = session_info.get('_isp', '')
        d['user_agent'] = session_info.get('_ua', '')
        d['ip'] = session_info.get('_ip', '')
        d['ref_domain'] = session_info.get('_ref', '')
        d['track_domain'] = session_info.get('_domain', '')

        custom_info = {}
        for k, v in session_info.iteritems():
            if k.startswith('_'):
                continue
            custom_info[k] = v

        d.update(custom_info)

        i = 1
        for offer in offers:
            d['offerurl%d'%i] = '/o1/%d_%d'%(cur_lpid, offer.id)
            i += 1

        i = 1
        for lander in landing_pages:
            d['lander%d'%i] = '/l1/%d'%i
            i += 1

        source_str = open(tmpl_path, 'r').read()

        global template_pool
        tmpl = template_pool.get_template_by_path(tmpl_path)
        try:
            s = tmpl.render(**d)
        except Exception, ex:
            self.check_pagesource_envs(source_str, d, cur_landing_page, cpid)

        self.check_pagesource_urls(source_str, uid, cur_landing_page, cpid)



if __name__ == '__main__':
    checker = CampaignChecker()
    checker.check_uid(int(sys.argv[1]))


