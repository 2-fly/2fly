#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import calendar
import hashlib
import time
import errno
import sys
import os
import ujson as json
from functools import wraps
from os import path as osp
from os import makedirs
from mako.template import Template
from flask import Flask, redirect, request, jsonify, make_response

import init_env
import settings
import views
import global_vars
from db_client import *
from utils import make_url, TemplateReader, jsonp, send_mail, get_model_uri, check_permission, decode_from_utf8
from view import Render, LoginRender, ModelView, BaseColumn, LandpageView
from views import source_view, campaign_view, user_view, offer_view, lander_view, admin_offer_view, mail_view, event_view, code_view
from global_vars import tmpl_reader, global_db_set as DBSet
from tools.campaign_checker import CampaignChecker
from commlib.db.db_tabledef import virus_domains_key, virusdomain_report_table, virusdomains_admin_table, gsb_admin_table
from commlib.utils.sig_helper import hmac_sha1_sig, verify_pay_callback_sig
from config.table_config import *
from config.permission_config import *
from config.auth_config import SUPER_ADMIN_USER_LIST

reload(sys)
sys.setdefaultencoding('utf-8')
sys.dont_write_bytecode = True

app = Flask(__name__, static_folder=settings.static_folder, static_url_path='/assets')
app.debug = settings.debug

timezone_offset = -time.timezone

PRODUCT_NAME = '2FlyTracking'

TIMEZONE = -time.timezone / 3600

def base_checker(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        DBSet.set_init(True)
        return func(*args, **kwargs)
    return decorated_function

def get_request_args():
    d1 = request.args.to_dict()
    d2 = request.form.to_dict()
    d1.update(d2)
    return d1

def gen_secret(passwd):
    return hashlib.md5(passwd + '_' + settings.app_secret).hexdigest()

def gen_md5(s):
    return hashlib.md5(s).hexdigest()

def gen_skey(username, password, time_str):
    s = '%s_%s_%s'%(username, password, time_str)
    return hashlib.md5(s).hexdigest()

def username2uid(username):
    user = DBSet.get_db_client().select_one(User, name=username)
    return user.id

def do_check_auth(*args, **kwargs):
    username = request.cookies.get('username')
    ts = request.cookies.get('time')
    skey = request.cookies.get('skey')

    if not username or not ts or not skey:
        return False

    if int(ts) + settings.cookies_expires < int(time.time()):
        return False

    users = DBSet.get_db_client().select_all(User, name=username)
    if not users:
        return False

    user = users[0]
    enc_skey = gen_skey(username, user.password, ts)
    if enc_skey != skey:
        return False
    else:
        return True

def do_check_auth_permission(permission_type, permission, *args, **kwargs):
    username = request.cookies.get('username')
    ts = request.cookies.get('time')
    skey = request.cookies.get('skey')

    if not username or not ts or not skey:
        return False, 0

    if int(ts) + settings.cookies_expires < int(time.time()):
        return False, 0

    users = DBSet.get_db_client().select_all(User, name=username)
    if not users:
        return False, 0

    user = users[0]
    enc_skey = gen_skey(username, user.password, ts)
    if enc_skey != skey:
        return False, 0
    # check permission
    check = check_permission(permission_type, user.permission, permission)
    return check, user.permission

def check_auth_permission(permission_type, permission):
    permission = permission or PERMISSION_IGNORE
    def check_auth(func):
        @wraps(func)
        def wrap_check_auth(*args, **kwargs):
            check, user_permission = do_check_auth_permission(permission_type, permission, *args, **kwargs)
            if not check:
                if user_permission == 3:
                    return redirect(global_vars.URL_OFFER_LIST)
                else:
                    return redirect('/')
            else:
                resp = func(*args, **kwargs)
                return resp
        return wrap_check_auth
    return check_auth

def check_auth_permission_args(permission_type, permission):
    permission = permission or PERMISSION_IGNORE
    def check_auth(func):
        @wraps(func)
        def wrap_check_auth(*args, **kwargs):
            check, user_permission = do_check_auth_permission(permission_type, permission, *args, **kwargs)
            if not check:
                if user_permission == 3:
                    return redirect(global_vars.URL_OFFER_LIST)
                else:
                    return redirect('/')
            else:
                resp = func(user_permission, *args, **kwargs)
                return resp
        return wrap_check_auth
    return check_auth

def check_auth(func):
    @wraps(func)
    def wrap_check_auth(*args, **kwargs):
        if not do_check_auth():
            return redirect('/')
        else:
            resp = func(*args, **kwargs)
            return resp
    return wrap_check_auth

def set_user_session(resp, username, password, ts):
    skey = gen_skey(username, password, ts)
    resp.set_cookie('username', username)
    resp.set_cookie('skey', skey)
    resp.set_cookie('time', str(ts))

def clear_user_session(resp):
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('skey', '', expires=0)
    resp.set_cookie('time', '', expires=0)

@app.route('/favicon.ico')
def handle_favicon():
    return ''

@app.route('/', methods=['GET'])
@base_checker
def handle_index():
    if do_check_auth():
        return redirect(global_vars.DEFAULT_INDEX_PAGE)

    render = LoginRender('Login %s'%PRODUCT_NAME, tmpl_reader)

    body_tmpl = tmpl_reader.read_file('login.tmpl')
    d = {
        'username' : '',
        'password' : '',
        'tips' : '',
    }
    body_str = Template(body_tmpl).render(**d)
    return render.gen_output(body_str)

@app.route('/', methods=['POST'])
@base_checker
def handle_login():
    args = get_request_args()
    username = args.get('username')
    password = args.get('password')

    if not username or not password:
        user = None
    else:
        hash_password = gen_secret(password)
        users = DBSet.get_db_client().select_all(User, name=username, password=hash_password)
        user = None
        if users:
            user = users[0]

    if user:
        resp = make_response(redirect(global_vars.DEFAULT_INDEX_PAGE))
        set_user_session(resp, username, hash_password, int(time.time()))
        return resp

    render = LoginRender('Login %s'%PRODUCT_NAME, tmpl_reader)
    body_tmpl = tmpl_reader.read_file('login.tmpl')
    tips = '''<div><span class="label label-important">Login failed</span></div>'''
    d = {
        'username' : username,
        'password' : '',
        'tips' : tips,
    }
    body_str = Template(body_tmpl).render(**d)
    return render.gen_output(body_str)

def verify_user_name(username):
    if DBSet.get_db_client().select_one(User, name=username):
        return False, None
    vfy_user = DBSet.get_db_client().select_one(VerifingUser, name=username)
    if vfy_user:
        if time.time() - vfy_user.timestamp > settings.mail_verify_timeout:
            return True, vfy_user
    else:
        return True, None
    return False, None

@app.route('/logout', methods=['GET', 'POST'])
def handle_logout():
    resp = make_response(redirect('/'))
    clear_user_session(resp)
    return resp

@app.route('/help', methods=['GET', 'POST'])
@base_checker
@check_auth
def handle_help():
    return views.handle_help_view(request.cookies)

###################################################################
####            User
###################################################################
@app.route(global_vars.URL_CHANGE_PWD, methods=['GET'])
@base_checker
@check_auth
def handle_change_password():
    view = user_view.UserView(request.cookies)
    return view.output_change_pwd()

@app.route(global_vars.URL_CHANGE_PWD, methods=['POST'])
@base_checker
@check_auth
def handle_save_password():
    view = user_view.UserView(request.cookies)
    return view.output_change_pwd(True)

@app.route(global_vars.URL_BASIC_INFO_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_DOMIAN_INFO)
def handle_basic_info_edit():
    view = user_view.UserView(request.cookies)
    return view.output_edit()

@app.route(global_vars.URL_BASIC_INFO_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_DOMIAN_INFO)
def handle_basic_info_save():
    view = user_view.UserView(request.cookies)
    return view.output_edit(save=True)

@app.route(global_vars.URL_BASIC_INFO_VERIFY_URL, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_DOMIAN_INFO)
def handle_verify_domains():
    username = request.cookies.get('username')
    view = user_view.UserView(request.cookies)
    return view.verify_domains(username)

@app.route(global_vars.URL_BASIC_INFO_VIRUS_URL, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_DOMIAN_INFO)
def handle_virus_domains():
    view = user_view.UserView(request.cookies)
    return view.virus_domains()


###################################################################
####            TrafficSource
###################################################################
@app.route(global_vars.URL_TS_FIELD, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_trafficsource_field():
    view = source_view.SourceView(request.cookies)
    s = view.get_source_field()
    return s

@app.route(global_vars.URL_TS_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_TRAFFIC_SOURCE)
def handle_trafficsource_list():
    username = request.cookies.get('username')
    my_uid = username2uid(username)
    view = ModelView(TrafficSource, request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_TS_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_TRAFFIC_SOURCE)
def handle_trafficsource_create1():
    view = source_view.SourceView(request.cookies)
    s = view.output_create()
    return s


@app.route(global_vars.URL_TS_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_TRAFFIC_SOURCE)
def handle_trafficsource_create2():
    view = source_view.SourceView(request.cookies)
    s = view.output_create(True)
    return s

@app.route(global_vars.URL_TS_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_TRAFFIC_SOURCE)
def handle_trafficsource_edit():
    view = source_view.SourceView(request.cookies)
    s = view.output_edit()
    return s

@app.route(global_vars.URL_TS_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_TRAFFIC_SOURCE)
def handle_trafficsource_edit2():
    view = source_view.SourceView(request.cookies)
    s = view.output_edit(True)
    return s

###################################################################
####            DomainGroup
###################################################################

@app.route(global_vars.URL_DG_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth
def handle_domaingroup_list():
    view = ModelView(DomainGroup, request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_DG_CREATE, methods=['GET'])
@base_checker
@check_auth
def handle_domaingroup_create1():
    view = ModelView(DomainGroup, request.cookies)
    s = view.output_create1()
    return s

@app.route(global_vars.URL_DG_CREATE, methods=['POST'])
@base_checker
@check_auth
def handle_domaingroup_create2():
    view = ModelView(DomainGroup, request.cookies)
    s = view.output_create2()
    return s


@app.route(global_vars.URL_DG_EDIT, methods=['GET'])
@base_checker
@check_auth
def handle_domaingroup_edit():
    view = ModelView(DomainGroup, request.cookies)
    s = view.output_edit1()
    return s

@app.route(global_vars.URL_DG_EDIT, methods=['POST'])
@base_checker
@check_auth
def handle_domaingroup_edit2():
    view = ModelView(DomainGroup, request.cookies)
    s = view.output_edit2()
    return s


###################################################################
####            AffiliateNetwork
###################################################################

@app.route(global_vars.URL_AFFNET_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_NETWORK)
def handle_affnetwork_list():
    view = ModelView(AffiliateNetwork, request.cookies)
    s = view.output_list()
    return s


@app.route(global_vars.URL_AFFNET_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_NETWORK)
def handle_affnetwork_create1():
    view = ModelView(AffiliateNetwork, request.cookies)
    s = view.output_create1()
    return s


@app.route(global_vars.URL_AFFNET_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_NETWORK)
def handle_affnetwork_create2():
    view = ModelView(AffiliateNetwork, request.cookies)
    s = view.output_create2()
    return s


@app.route(global_vars.URL_AFFNET_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_NETWORK)
def handle_affnetwork_edit():
    view = ModelView(AffiliateNetwork, request.cookies)
    s = view.output_edit1()
    return s

@app.route(global_vars.URL_AFFNET_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_NETWORK)
def handle_affnetwork_edit2():
    view = ModelView(AffiliateNetwork, request.cookies)
    s = view.output_edit2()
    return s


###################################################################
####            Offer
###################################################################
@app.route(global_vars.URL_OFFER_SET_HIDDEN, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ALL_OFFER)
def handle_offer_set_hidden():
    view = offer_view.OfferView(request.cookies)
    s = view.set_hidden()
    return s

@app.route(global_vars.URL_OFFER_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ALL_OFFER)
def handle_offer_list():
    view = offer_view.OfferView(request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_OFFER_CREATE_JSON, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ALL_OFFER)
def handle_offer_create_json():
    view = offer_view.OfferView(request.cookies)
    return view.create_return_json()


@app.route(global_vars.URL_OFFER_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ALL_OFFER)
def handle_offer_create1():
    view = offer_view.OfferView(request.cookies)
    s = view.output_create()
    return s


@app.route(global_vars.URL_OFFER_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ALL_OFFER)
def handle_offer_create2():
    view = offer_view.OfferView(request.cookies)
    s = view.output_create(True)
    return s


@app.route(global_vars.URL_OFFER_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ALL_OFFER)
def handle_offer_edit():
    view = offer_view.OfferView(request.cookies)
    s = view.edit()
    return s

@app.route(global_vars.URL_OFFER_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ALL_OFFER)
def handle_offer_edit2():
    view = offer_view.OfferView(request.cookies)
    s = view.edit(True)
    return s


###################################################################
####            LandingPage
###################################################################

@app.route(global_vars.URL_LP_SET_HIDDEN, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_LANDPAGE)
def handle_lp_set_hidden():
    view = lander_view.LanderView(request.cookies)
    s = view.set_hidden()
    return s

@app.route(global_vars.URL_LP_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_LANDPAGE)
def handle_lp_list():
    view = lander_view.LanderView(request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_LP_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_LANDPAGE)
def handle_lp_create1():
    view = LandpageView(LandingPage, request.cookies)
    s = view.output_lp_html(0)
    return s


@app.route(global_vars.URL_LP_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_LANDPAGE)
def handle_lp_create2():
    view = LandpageView(LandingPage, request.cookies)
    s = view.output_lp_html(1)
    return s


@app.route(global_vars.URL_LP_CREATE_JSON, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_LANDPAGE)
def handle_lp_create_json():
    view = lander_view.LanderView(request.cookies)
    return view.create_return_json()


@app.route(global_vars.URL_LP_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_LANDPAGE)
def handle_lp_edit():
    view = LandpageView(LandingPage, request.cookies)
    s = view.output_lp_html(2)
    return s

@app.route(global_vars.URL_LP_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_LANDPAGE)
def handle_lp_edit2():
    view = LandpageView(LandingPage, request.cookies)
    s = view.output_lp_html(3)
    return s

@app.route(global_vars.URL_LP_BATCH_UPLOAD, methods=['GET', 'POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_LANDPAGE)
def handle_lp_batchupload():
    view = lander_view.LanderView(request.cookies)
    s = view.output_batch_upload()
    return s

###################################################################
####            Path
###################################################################

@app.route(global_vars.URL_PATH_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_path_list():
    view = ModelView(Path, request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_PATH_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_path_create1():
    view = ModelView(Path, request.cookies)
    s = view.output_create1()
    return s

@app.route(global_vars.URL_PATH_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_path_create2():
    view = ModelView(Path, request.cookies)
    s = view.output_create2()
    return s

@app.route(global_vars.URL_PATH_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_path_edit():
    view = ModelView(Path, request.cookies)
    s = view.output_edit1()
    return s

@app.route(global_vars.URL_PATH_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_path_edit2():
    view = ModelView(Path, request.cookies)
    s = view.output_edit2()
    return s


###################################################################
####            SwapRotation
###################################################################

@app.route(global_vars.URL_SWAP_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_swap_list():
    view = ModelView(SwapRotation, request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_SWAP_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_swap_create1():
    view = ModelView(SwapRotation, request.cookies)
    s = view.output_create1()
    return s

@app.route(global_vars.URL_SWAP_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_swap_create2():
    view = ModelView(SwapRotation, request.cookies)
    s = view.output_create2()
    return s

@app.route(global_vars.URL_SWAP_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_swap_edit():
    view = ModelView(SwapRotation, request.cookies)
    s = view.output_edit1()
    return s

@app.route(global_vars.URL_SWAP_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_swap_edit2():
    view = ModelView(SwapRotation, request.cookies)
    s = view.output_edit2()
    return s

###################################################################
####            Campaign
###################################################################
@app.route(global_vars.URL_CAMP_CHECK_OFFER, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_chekc_offer():
    ret = campaign_view.CampaignView.check_offer_country(request.cookies)
    return jsonify(ret)

@app.route(global_vars.URL_CAMP_GET_RULE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_get_rule():
    json = campaign_view.CampaignView.get_rule(request.cookies)
    return json

@app.route(global_vars.URL_CAMP_RULE_SEC_CATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_rule_config_sec_cate():
    json = campaign_view.CampaignView.get_sec_cate_json()
    return json

@app.route(global_vars.URL_CAMP_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_campaign_list():
    view = campaign_view.CampaignView(request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_CAMP_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_campaign_create1():
    view = campaign_view.CampaignView(request.cookies)
    s = view.output_create(False, '', '')
    return s


@app.route(global_vars.URL_CAMP_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_campaign_create2():
    view = campaign_view.CampaignView(request.cookies)
    s = view.output_create(True)
    return s


@app.route(global_vars.URL_CAMP_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_campaign_edit():
    view = campaign_view.CampaignView(request.cookies)
    s = view.output_edit1()
    return s

@app.route(global_vars.URL_CAMP_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_campaign_edit2():
    view = campaign_view.CampaignView(request.cookies)
    s = view.output_edit2()
    return s

@app.route(global_vars.URL_CAMP_SET_HIDDEN, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_set_campaign_hidden():
    view = campaign_view.CampaignView(request.cookies)
    s = view.set_hidden()
    return s

@app.route('/api/update_campaign_cost.json')
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
@jsonp
def handle_update_campaign_cost():
    args = get_request_args()
    cpid = int(args.get("cpid",0))
    start_time = args.get("start_time", "")
    timezone = int(args.get("timezone", TIMEZONE))
    payout = float(args.get("payout", 0))
    campaign_view.CampaignView.update_campaign_cost(request.cookies, cpid, start_time, timezone, payout)
    return jsonify({})

@app.route('/api/update_campaign_cost_history.json')
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
@jsonp
def handle_update_campaign_cost_history():
    args = get_request_args()
    cpid = int(args.get("cpid",0))
    result = campaign_view.CampaignView.get_campaign_update_list(request.cookies, cpid)
    data = {
        "campaign" : result
    }
    return jsonify(data)

@app.route(global_vars.URL_SWITCH_PATH_GET, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_SWITCH_PATH)
def handle_get_switch_path():
    view = campaign_view.CampaignView(request.cookies)
    return view.get_switch_path()

@app.route(global_vars.URL_SWITCH_PATH_SAVE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_SWITCH_PATH)
def handle_save_switch_path():
    view = campaign_view.CampaignView(request.cookies)
    return view.save_switch_path()

###################################################################
####           AdminOffer
###################################################################

@app.route(global_vars.URL_ADMIN_OFFER_SET_HIDDEN, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_OFFER)
def handle_admin_offer_set_hidden():
    view = admin_offer_view.AdminOfferView(request.cookies)
    s = view.set_hidden()
    return s

@app.route(global_vars.URL_ADMIN_OFFER_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_OFFER)
def handle_admin_offer_list():
    view = admin_offer_view.AdminOfferView(request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_ADMIN_OFFER_CREATE_JSON, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_OFFER)
def handle_admin_offer_create_json():
    view = admin_offer_view.AdminOfferView(request.cookies)
    return view.create_return_json()

@app.route(global_vars.URL_ADMIN_OFFER_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_OFFER)
def handle_admin_offer_create1():
    view = admin_offer_view.AdminOfferView(request.cookies)
    s = view.output_create()
    return s

@app.route(global_vars.URL_ADMIN_OFFER_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_OFFER)
def handle_admin_offer_create2():
    view = admin_offer_view.AdminOfferView(request.cookies)
    s = view.output_create(True)
    return s

@app.route(global_vars.URL_ADMIN_OFFER_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_OFFER)
def handle_admin_offer_edit():
    view = admin_offer_view.AdminOfferView(request.cookies)
    s = view.edit()
    return s

@app.route(global_vars.URL_ADMIN_OFFER_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_OFFER)
def handle_admin_offer_edit2():
    view = admin_offer_view.AdminOfferView(request.cookies)
    s = view.edit(True)
    return s

###################################################################
####            AdminTrafficSource
###################################################################
@app.route(global_vars.URL_ADMIN_TS_FIELD, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
def handle_admin_trafficsource_field():
    view = source_view.AdminSourceView(request.cookies)
    s = view.get_source_field()
    return s

@app.route(global_vars.URL_ADMIN_TS_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_TRAFFIC_SOURCE)
def handle_admin_trafficsource_list():
    username = request.cookies.get('username')
    my_uid = username2uid(username)
    view = ModelView(AdminTrafficSource, request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_ADMIN_TS_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_TRAFFIC_SOURCE)
def handle_admin_trafficsource_create1():
    view = source_view.AdminSourceView(request.cookies)
    s = view.output_create()
    return s

@app.route(global_vars.URL_ADMIN_TS_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_TRAFFIC_SOURCE)
def handle_admin_trafficsource_create2():
    view = source_view.AdminSourceView(request.cookies)
    s = view.output_create(True)
    return s

@app.route(global_vars.URL_ADMIN_TS_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_TRAFFIC_SOURCE)
def handle_admin_trafficsource_edit():
    view = source_view.AdminSourceView(request.cookies)
    s = view.output_edit()
    return s

@app.route(global_vars.URL_ADMIN_TS_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_TRAFFIC_SOURCE)
def handle_admin_trafficsource_edit2():
    view = source_view.AdminSourceView(request.cookies)
    s = view.output_edit(True)
    return s

###################################################################
####            AdminAffiliateNetwork
###################################################################

@app.route(global_vars.URL_ADMIN_AFFNET_LIST, methods=['POST', 'GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_AFFILIATE_NETWORK)
def handle_admin_affnetwork_list():
    view = ModelView(AdminAffiliateNetwork, request.cookies)
    s = view.output_list()
    return s

@app.route(global_vars.URL_ADMIN_AFFNET_CREATE, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_AFFILIATE_NETWORK)
def handle_admin_affnetwork_create1():
    view = ModelView(AdminAffiliateNetwork, request.cookies)
    s = view.output_create1()
    return s

@app.route(global_vars.URL_ADMIN_AFFNET_CREATE, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_AFFILIATE_NETWORK)
def handle_admin_affnetwork_create2():
    view = ModelView(AdminAffiliateNetwork, request.cookies)
    s = view.output_create2()
    return s

@app.route(global_vars.URL_ADMIN_AFFNET_EDIT, methods=['GET'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_AFFILIATE_NETWORK)
def handle_admin_affnetwork_edit():
    view = ModelView(AdminAffiliateNetwork, request.cookies)
    s = view.output_edit1()
    return s

@app.route(global_vars.URL_ADMIN_AFFNET_EDIT, methods=['POST'])
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_ADMIN_AFFILIATE_NETWORK)
def handle_admin_affnetwork_edit2():
    view = ModelView(AdminAffiliateNetwork, request.cookies)
    s = view.output_edit2()
    return s

def mkdir_p(path):
    try:
        makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and osp.isdir(path):
            pass
        else:
            raise

###################################################################
####           Check Campaign 
###################################################################
@app.route(global_vars.URL_CHECK_CAMPAIGN)
@base_checker
@check_auth_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_CAMPAIGN)
@jsonp
def handle_campaign_check():
    args = get_request_args()
    username = request.cookies.get('username')
    my_uid = username2uid(username)
    cpid = int(args['cpid'])
    checker = CampaignChecker()
    checker.check_campaign(my_uid, cpid)
    args = checker.gen_output(my_uid)
    view = LandpageView(LandingPage, request.cookies)
    s = view.output_campaign_check(args)
    return s
    return args

###################################################################
####           Event  
###################################################################
@app.route(global_vars.URL_EVENTS_EDIT, methods=['GET', 'POST'])
@base_checker
@check_auth_permission(PERMISSION_TOOLS, PERMISSION_TOOLS_EVENTS)
def handle_events_edit():
    view = event_view.EventView(request.cookies)
    return view.output_event_create(False)

@app.route(global_vars.URL_EVENTS_CREATE, methods=['GET', 'POST'])
@base_checker
@check_auth_permission(PERMISSION_TOOLS, PERMISSION_TOOLS_EVENTS)
def handle_events_create():
    view = event_view.EventView(request.cookies)
    return view.output_event_view()

@app.route(global_vars.URL_EVENTS_LIST)
@base_checker
@check_auth_permission(PERMISSION_TOOLS, PERMISSION_TOOLS_EVENTS)
def handle_events_list():
    view = event_view.EventView(request.cookies)
    return view.output_event_list()

@app.route(global_vars.URL_EVENTS_CONFIG, methods=['GET', 'POST'])
@base_checker
@check_auth_permission(PERMISSION_TOOLS, PERMISSION_TOOLS_EVENTS)
def handle_events_config():
    view = event_view.EventView(request.cookies)
    return view.output_event_config()

@app.route(global_vars.URL_RELATIVE_EVENTS_EDIT, methods=['GET', 'POST'])
@base_checker
@check_auth_permission(PERMISSION_TOOLS, PERMISSION_TOOLS_RELATIVE_EVENTS)
def handle_relative_events_edit():
    view = event_view.AdminEventView(request.cookies)
    return view.output_event_create(False)

@app.route(global_vars.URL_RELATIVE_EVENTS_CREATE, methods=['GET', 'POST'])
@base_checker
@check_auth_permission(PERMISSION_TOOLS, PERMISSION_TOOLS_RELATIVE_EVENTS)
def handle_relative_events_create():
    view = event_view.AdminEventView(request.cookies)
    return view.output_event_view()

@app.route(global_vars.URL_TOOLS_DECRYPT_EDIT, methods=['GET', 'POST'])
@base_checker
@check_auth_permission(PERMISSION_TOOLS, PERMISSION_TOOLS_DECRYPT)
def handle_decrypt_edit():
    model = code_view.CodeView(request.cookies)
    args = get_request_args()
    encode = args.get("encode_list", "")
    decode = args.get("decode_list", "")
    op = args.get("submit", None)
    return model.output_edit(encode, decode, op)

#################################################################
@app.route('/test', methods=['GET'])
@base_checker
def handle_test():
    render = LoginRender('Login Test', tmpl_reader)

    body_tmpl = tmpl_reader.read_file('test.tmpl')
    d = {}
    body_str = Template(body_tmpl).render(**d)
    return render.gen_output(body_str)

###################################################################
####          verify 
###################################################################
def check_sync_redis(url):
    args = request.args.to_dict()
    t = int(args.get("time", 0))
    sign = args.get("sig", "")
    if not sign or time.time() - t > 5 * 60:
        return False
    return verify_pay_callback_sig(global_vars.APP_KEY, request.method, url, args)

@app.route(global_vars.URL_VIRUS_SYNC, methods=['POST', 'GET'])
@base_checker
def handle_virus_sync():
    args = request.form.to_dict()
    if not check_sync_redis(global_vars.URL_VIRUS_SYNC):
        return "sign error"
    else:
        data = args.get("data", "")
        if not data:
            return "data error"
        data = json.loads(data)
        db_key = virusdomains_admin_table
        redis_cli = global_vars.global_db_set.get_redis_db()

        for d in data:
            obj = json.loads(d)
            redis_cli.add_one(db_key, obj['domain'], obj['res'])
        return "ok"

@app.route(global_vars.URL_GSB_SYNC, methods=["POST"])
@base_checker
def handle_gsb_sync():
    args = request.form.to_dict()
    if not check_sync_redis(global_vars.URL_GSB_SYNC):
        return "sign error"
    else:
        data = args.get("data", "")
        if not data:
            return "data error"
        db_key = gsb_admin_table
        redis_cli = global_vars.global_db_set.get_redis_db()
        data = json.loads(data)
        for _domain, res in data.iteritems():
            redis_cli.add_one(db_key, _domain, json.dumps(res))
        return "ok"

if __name__ == '__main__':
    app.run(settings.bind_ip, settings.bind_port)

