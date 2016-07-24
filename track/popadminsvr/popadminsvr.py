#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import calendar
import time
import errno
import sys
from functools import wraps
from os import path as osp
from os import makedirs

import ujson as json
from mako.template import Template
from flask import Flask, redirect, request, jsonify, make_response, Response

import init_env
import settings
import global_vars
import models
from views import login, website_view, campaign_view, report_view, view_utils, user_view, img_mgr_view
from db_client import *
from utils import make_url, TemplateReader, jsonp, send_mail, gen_skey, gen_secret, get_request_args
from global_vars import tmpl_reader, global_db_set as DBSet
import global_vars
from commlib.utils.utils import LoadTimeList, DAY_TYPE_FULL, DAY_TYPE_PART
from config import table_config

PRODUCT_NAME = "PopAdvertise"

reload(sys)
sys.setdefaultencoding('utf-8')
sys.dont_write_bytecode = True

app = Flask(__name__, static_folder=settings.static_folder, static_url_path='/assets')
app.debug = settings.debug

def set_user_session(resp, username, password, ts, t):
    skey = gen_skey(username, password, ts)
    resp.set_cookie('username', username)
    resp.set_cookie('skey', skey)
    resp.set_cookie('time', str(ts))
    resp.set_cookie("type", str(t))

def clear_user_session(resp):
    resp.set_cookie('username', "")
    resp.set_cookie('skey', "")
    resp.set_cookie('time', "")
    resp.set_cookie("type", "")

def base_checker(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        DBSet.set_init(True)
        return func(*args, **kwargs)
    return decorated_function




def check_auth(func):
    @wraps(func)
    def wrap_check_auth(*args, **kwargs):
        if not do_check_auth():
            if request.headers.get("Transform-Type", "") == "pjax":
                return jsonify({"error":"login"})
            else:
                return redirect('/')
        else:
            return func(*args, **kwargs)
    return wrap_check_auth

def check_publiser(func):
    @wraps(func)
    def wrap_check_publiser(*args, **kwargs):
        t = request.cookies.get('type')
        if not t or not t.isdigit() or int(t) != global_vars.PUBLISHER:
            return redirect("/")
        else:
            return func(*args, **kwargs)
    return wrap_check_publiser

def check_advertiser(func):
    @wraps(func)
    def wrap_check_advertiser(*args, **kwargs):
        t = request.cookies.get('type')
        if not t or not t.isdigit() or int(t) != global_vars.ADVERTISER:
            return redirect("/")
        else:
            return func(*args, **kwargs)
    return wrap_check_advertiser

def do_check_auth(*args, **kwargs):
    username = request.cookies.get('username')
    ts = request.cookies.get('time')
    t = request.cookies.get('type')
    skey = request.cookies.get('skey')

    if not t or not t.isdigit() or not username or not ts or not skey:
        return False

    t = int(t)

    if int(ts) + settings.cookies_expires < int(time.time()):
        return False

    cls = Publisher if t == global_vars.PUBLISHER else Advertiser
    db_client = DBSet.get_db_client()
    users = db_client.select_all(cls, name=username)
    if not users:
        return False

    user = users[0]
    enc_skey = gen_skey(username, user.password, ts)
    if enc_skey != skey:
        return False
    else:
        return True
def pjax(url):
    def init_nav(func):
        @wraps(func)
        def wrap_init_nav(*args, **kwargs):
            body = func(*args, **kwargs)
            if request.headers.get("Transform-Type", "") == "pjax":
                return jsonify(body) if type(body) == dict else body
            else:
                if isinstance(body, Response):
                    return body
                else:
                    body_str = body['html'] if type(body) == dict else body
                    render = view_utils.Render('Mobitx', tmpl_reader, request.cookies)
                    return render.gen_output(body_str, {'nav_left' : view_utils.to_links(url, request.cookies.get('type'))})
        return wrap_init_nav
    return init_nav

@app.route("/", methods=["GET"])
@base_checker
def handle_index():
    if do_check_auth():
        return redirect(global_vars.URL_CAMP_REPORT)
    render = login.LoginRender('Login %s'%PRODUCT_NAME, tmpl_reader)
    body_tmpl = tmpl_reader.read_file('login.tmpl')
    body_str = Template(body_tmpl).render(tips="", publisher_val=global_vars.PUBLISHER, advertiser_val=global_vars.ADVERTISER)
    return render.gen_output(body_str)

@app.route("/", methods=['POST'])
@base_checker
def handle_login():
    args = get_request_args()
    username = args.get('username')
    password = gen_secret(args.get('password'))
    t = int(args['type'])
    res = login.login(username, password, t)


    if res:
        resp = make_response(redirect(global_vars.URL_CAMP_REPORT))
        set_user_session(resp, username, password, int(time.time()), t)
        return resp

    render = login.LoginRender('Login %s'%PRODUCT_NAME, tmpl_reader)
    body_tmpl = tmpl_reader.read_file('login.tmpl')
    tips = '''<div><span class="label label-important">Login failed</span></div>'''
    d = {
        'username' : username,
        'password' : '',
        'tips' : tips,
        'publisher_val':global_vars.PUBLISHER,
        'advertiser_val':global_vars.ADVERTISER,
    }
    body_str = Template(body_tmpl).render(**d)
    return render.gen_output(body_str)

@app.route(global_vars.URL_MODIFY_USER, methods=['GET'])
@base_checker
@check_auth
@pjax(global_vars.URL_MODIFY_USER)
def handle_modify_user1():
    view = user_view.UserView(request.cookies)
    return view.get_account()

@app.route(global_vars.URL_MODIFY_USER, methods=['POST'])
@base_checker
@check_auth
@pjax(global_vars.URL_MODIFY_USER)
def handle_modify_user2():
    view = user_view.UserView(request.cookies)
    return view.modify_account()

@app.route(global_vars.URL_DEFAULT)
@base_checker
@check_auth
@pjax(global_vars.URL_DEFAULT)
def handle_default():
    view = website_view.WebsiteView(request.cookies)
    return view.test()

@app.route(global_vars.URL_LOGOUT, methods=["GET"])
@base_checker
@check_auth
def handle_logout():
    resp = make_response(redirect('/'))
    clear_user_session(resp)
    return resp
#########################################################################
####            image manager
#########################################################################
@app.route(global_vars.URL_IMG_MGR, methods=["GET"])
@base_checker
@check_auth
@check_advertiser
@pjax(global_vars.URL_IMG_MGR)
def handle_img_mgr():
    view = img_mgr_view.ImgMgrView(request.cookies)
    return view.output_view()

@app.route(global_vars.URL_IMG_OP, methods=["GET", "POST"])
@base_checker
@check_auth
@check_advertiser
def handle_img_op():
    view = img_mgr_view.ImgMgrView(request.cookies)
    return view.handler_file_op()

#########################################################################
####            website
#########################################################################
@app.route(global_vars.URL_WEBSITE_LIST, methods=["GET"])
@base_checker
@check_auth
@check_publiser
@pjax(global_vars.URL_WEBSITE_LIST)
def handle_website_list():
    view = website_view.WebsiteView(request.cookies)
    return view.output_list()

@app.route(global_vars.URL_WEBSITE_ADD, methods=['GET'])
@base_checker
@check_auth
@check_publiser
@pjax(global_vars.URL_WEBSITE_LIST)
def handle_website_add1():
    view = website_view.WebsiteView(request.cookies)
    return view.output_add()

@app.route(global_vars.URL_WEBSITE_ADD, methods=['POST'])
@base_checker
@check_auth
@check_publiser
def handle_website_add2():
    view = website_view.WebsiteView(request.cookies)
    return view.output_add(save=True)

@app.route(global_vars.URL_WEBSITE_EDIT, methods=['GET'])
@base_checker
@check_auth
@check_publiser
@pjax(global_vars.URL_WEBSITE_EDIT)
def handle_website_edit1():
    view = website_view.WebsiteView(request.cookies)
    return view.output_edit()

@app.route(global_vars.URL_WEBSITE_EDIT, methods=['POST'])
@base_checker
@check_auth
@check_publiser
@pjax(global_vars.URL_WEBSITE_EDIT)
def handle_website_edit2():
    view = website_view.WebsiteView(request.cookies)
    return view.output_edit(save=True)

@app.route(global_vars.URL_WEBSITE_BID_LIST, methods=["GET"])
@base_checker
@check_auth
@check_publiser
@pjax(global_vars.URL_WEBSITE_BID_LIST)
def handle_website_bid_list():
    view = website_view.WebsiteView(request.cookies)
    return view.bid_list()

@app.route(global_vars.URL_WEBSITE_BID_EDIT, methods=["GET"])
@base_checker
@check_auth
@check_publiser
@pjax(global_vars.URL_WEBSITE_BID_EDIT)
def handle_website_bid_edit1():
    view = website_view.WebsiteView(request.cookies)
    return view.bid_edit()

@app.route(global_vars.URL_WEBSITE_BID_EDIT, methods=["POST"])
@base_checker
@check_auth
@check_publiser
@pjax(global_vars.URL_WEBSITE_BID_EDIT)
def handle_website_bid_edit2():
    view = website_view.WebsiteView(request.cookies)
    return view.bid_edit(save=True)

@app.route(global_vars.URL_WEBSITE_BID_ADD, methods=["GET"])
@base_checker
@check_auth
@check_publiser
@pjax(global_vars.URL_WEBSITE_BID_ADD)
def handle_website_bid_add1():
    view = website_view.WebsiteView(request.cookies)
    return view.bid_add()

@app.route(global_vars.URL_WEBSITE_BID_ADD, methods=["POST"])
@base_checker
@check_auth
@check_publiser
def handle_website_bid_add2():
    view = website_view.WebsiteView(request.cookies)
    return view.bid_add(save=True)


#########################################################################
####            campaign
#########################################################################
@app.route(global_vars.URL_CAMP_LIST, methods=["GET"])
@base_checker
@check_auth
@check_advertiser
@pjax(global_vars.URL_CAMP_LIST)
def handle_camp_list():
    view = campaign_view.CampaignView(request.cookies)
    return view.list()

@app.route(global_vars.URL_CAMP_ADD, methods=["GET"])
@base_checker
@check_auth
@check_advertiser
@pjax(global_vars.URL_CAMP_ADD)
def handle_camp_add1():
    view = campaign_view.CampaignView(request.cookies)
    return view.add()

@app.route(global_vars.URL_CAMP_ADD, methods=["POST"])
@base_checker
@check_auth
@check_advertiser
@pjax(global_vars.URL_CAMP_ADD)
def handle_camp_add2():
    view = campaign_view.CampaignView(request.cookies)
    return view.add(save=True)

@app.route(global_vars.URL_CAMP_EDIT, methods=["GET"])
@base_checker
@check_auth
@check_advertiser
@pjax(global_vars.URL_CAMP_EDIT)
def handle_camp_edit1():
    view = campaign_view.CampaignView(request.cookies)
    return view.edit()

@app.route(global_vars.URL_CAMP_EDIT, methods=["POST"])
@base_checker
@check_auth
@check_advertiser
@pjax(global_vars.URL_CAMP_EDIT)
def handle_camp_edit2():
    view = campaign_view.CampaignView(request.cookies)
    return view.edit(save=True)

@app.route(global_vars.URL_UPLOAD_JS_AC, methods=["GET"])
@base_checker
@check_auth
@check_advertiser
def handle_camp_upload_js_ac():
    view = campaign_view.CampaignView(request.cookies)
    return view.upload_js_ac()

@app.route(global_vars.URL_CAMP_REPORT)
@base_checker
@check_auth
@pjax(global_vars.URL_CAMP_REPORT)
def handle_reports_campaign():
    tags = [
        table_config.table_config[table_config.CAMPAIGN_TAG],
    ]
    chart_tags = []
    #return report_view.handle_inner_report(tags, global_vars.URL_CAMP_REPORT, request.cookies, tmpl="camp_report.tmpl")
    return report_view.handle_report_grid(tags, chart_tags, global_vars.URL_CAMP_REPORT, request.cookies, tmpl="new_report.tmpl")

@app.route(global_vars.URL_CAMP_DATE_REPORT)
@base_checker
@check_auth
@pjax(global_vars.URL_CAMP_DATE_REPORT)
def handle_reports_campaign_date():
    tags = [
        table_config.table_config[table_config.CAMPAIGN_DATE_TAG],
        table_config.table_config[table_config.CAMPAIGN_HOUR_TAG],
        table_config.table_config[table_config.WEBSITE_TAG],
        table_config.table_config[table_config.BANNER_TAG],
        table_config.table_config[table_config.OS_TAG],
        table_config.table_config[table_config.COUNTRY_TAG],
        table_config.table_config[table_config.BROWSER_TAG]
    ]
    chart_tags = [
        table_config.table_config[table_config.CAMPAIGN_HOUR_TAG]
    ]
    args = get_request_args()
    return report_view.handle_report_grid(tags, chart_tags, global_vars.URL_CAMP_DATE_REPORT, request.cookies, args=args, tmpl="new_report.tmpl")

@app.route("/campaign/switch", methods=["GET"])
@base_checker
@check_auth
@check_advertiser
def handle_change_camp_status():
    args = get_request_args()
    try:
        cid = int(args["cid"])
        status = int(args['status'])
        assert status in [0, 1]
    except:
        return "0"
    view = campaign_view.CampaignView(request.cookies)
    return "1" if view.change_camp_status(cid, status) else "0"


@app.route(global_vars.URL_CHANGE_WEBSITE_BID, methods=['POST'])
@base_checker
@check_auth
@check_advertiser
def handle_change_website_bid():
    args = get_request_args()
    datas = []
    for e in args['data'].split(","):
        websiteid, bid, budget = e.split(":")
        if not bid or bid == "auto":
            bid = -1
        else:
            if not bid.replace(".", "").isdigit():
                return jsonify({"ret":False})
            bid = float(bid)
        if not budget or budget == "unlimited":
            budget = -1
        else:
            if not budget.replace(".", "").isdigit():
                return jsonify({'ret':False})
            budget = float(budget)
        datas.append((websiteid, bid, budget))

    cpid = args['cpid']
    if not cpid.isdigit():
        return jsonify({"ret":False})
    cpid = int(cpid)
    db_cli = DBSet.get_db_client()
    camp = db_cli.select_one(Campaign, id=cpid)
    l = []
    if camp.website_info_list:
        l = [e for e in camp.website_info_list.split(",") if len(e.split(";")) == 3]
    wid_info_map = {}
    for e in l:
        wid_info_map[e.split(";")[0]] = e

    for wid, bid, budget in datas:
        if wid in wid_info_map and bid == -1 and budget == -1:
            wid_info_map.pop(wid)
        else:
            wid_info_map[wid] = ";".join([wid, str(bid), str(budget)])
    camp.website_info_list = ""
    if wid_info_map:
        camp.website_info_list = ",".join(wid_info_map.values())
    db_cli.do_save(camp)

    return jsonify({"ret": True})

@app.route(global_vars.URL_FILTER_WEBSITE_REPORT, methods=["GET"])
@base_checker
@check_auth
@check_advertiser
@jsonp
def handle_filter_website_report():
    args = get_request_args()
    hours = int(args['hour'])
    cpid = int(args['cpid'])
    rules = make_rules(args)

    username = request.cookies.get('username')
    user_type = request.cookies.get('type')
    my_uid = view_utils.username2uid(username, user_type, DBSet.get_db_client())
    cp_names = __load_campaign_names(my_uid)

    ins = ws_rpt.WebsiteResult()
    ins.set_uid(my_uid)
    ins.set_rules(rules)
    ins.set_cpnames(cp_names)
    ins.init_data()
    data = ins.load_hour_result(hours, args)
    return jsonify({"data":data})

@app.route(global_vars.URL_CHANGE_CAMP_WEBSITE_LIST, methods=["GET"])
@base_checker
@check_auth
@check_advertiser
@jsonp
def handle_change_camp_website():
    args = get_request_args()
    cpid = int(args['cpid'])
    wb_list = args.get('list', "")
    op_type = args['op_type']
    if not wb_list:
        return jsonify({'ret':0})

    view = campaign_view.CampaignView(request.cookies)
    ret = view.change_website_list(cpid, op_type, wb_list.split(","))

    return jsonify({"ret":1 if ret else 0})

@app.route('/api/async/summary/chart')
@base_checker
@check_auth
@check_advertiser
@jsonp
def handle_async_summary_chart():
    args = get_request_args()
    tag = args['tag']
    class_ins = models.STATIC_RESULT_TYPE_CLASS.get(tag, None)

    time_str = args.get("time", '')
    timezone = int(args.get("timezone", report_view.TIMEZONE))
    username = request.cookies.get('username')
    user_type = global_vars.ADVERTISER
    my_uid = view_utils.username2uid(username, user_type, DBSet.get_db_client())
    if my_uid in settings.admin_white_uid_list:
        select_username = args.get("username", username)
        select_username = select_username if select_username != "" else username
        my_uid = view_utils.username2uid(select_username, user_type, DBSet.get_db_client())

    start_hour = int(args.get("start_hour", "0"))
    end_hour = int(args.get("end_hour", "23"))
    rules = make_rules(args)
    cp_names = __load_campaign_names(my_uid)
    ins = class_ins()
    ins.set_uid(my_uid)
    ins.parse_time(time_str)
    ins.set_hour(start_hour, end_hour)
    ins.set_rules(rules)
    ins.set_timezone(timezone)
    ins.set_cpnames(cp_names)
    ins.init_data()
    ins.load_result()
    data= ins.get_kendo_charts()
    return json.dumps(data)

@app.route('/api/async/summary')
@base_checker
@check_auth
@check_advertiser
@jsonp
def handle_async_summary():
    args = get_request_args()
    tag = args['tag']
    class_ins = models.STATIC_RESULT_TYPE_CLASS.get(tag, None)

    time_str = args.get("time", '')
    start_hour = int(args.get("start_hour", "0"))
    end_hour = int(args.get("end_hour", "23"))
    timezone = int(args.get("timezone", report_view.TIMEZONE))
    username = request.cookies.get('username')
    user_type = global_vars.ADVERTISER
    my_uid = view_utils.username2uid(username, user_type, DBSet.get_db_client())
    if my_uid in settings.admin_white_uid_list:
        select_username = args.get("username", username)
        select_username = select_username if select_username != "" else username
        my_uid = view_utils.username2uid(select_username, user_type, DBSet.get_db_client())

    rules = make_rules(args)
    cp_names = __load_campaign_names(my_uid)
    ins = class_ins()
    ins.set_uid(my_uid)
    ins.parse_time(time_str)
    ins.set_hour(start_hour, end_hour)
    ins.set_rules(rules)
    ins.set_timezone(timezone)
    ins.set_cpnames(cp_names)
    ins.init_data()
    data= ins.get_kendo_async_data(args)
    return json.dumps(data)

@app.route('/api/summary.json')
@base_checker
@check_auth
@jsonp
def handle_summary():
    args = get_request_args()
    # parse start & end time
    time_str = args.get("time", '')
    timezone = int(args.get("timezone", report_view.TIMEZONE))
    username = request.cookies.get('username')
    user_type = request.cookies.get('type')

    my_uid = view_utils.username2uid(username, user_type, DBSet.get_db_client())
    tags_str = args.get("tags", "")
    tags = tags_str.split(",")
    select_username = username
    if my_uid in settings.admin_white_uid_list:
        select_username = args.get("username", username)
        select_username = select_username if select_username != "" else username
        my_uid = view_utils.username2uid(select_username, user_type, DBSet.get_db_client())

    _type = args.get("type", "normal")
    if _type == "update_cost":
        pass
    rules = make_rules(args)
    table_data = load_table_data(my_uid, time_str, timezone, tags, rules)
    # json response
    pv_records = []
    finance_records = []
    pv_items = ['visits', 'clicks']
    finance_items = ['conversions', 'profit', 'revenue', 'cost']

    click_sum = 0#int(result.clicks)
    visit_sum = 0#int(result.visits)
    conversion_sum = 0#int(result.conversions)

    data = {
        'records1' : pv_records,
        'records2' : finance_records,
        'visit_sum' : 0,#int(result.visits),
        'profit_sum' : 0, #int(result.profit),
        'cost_sum' : 0, #int(result.cost),
        'revenue_sum' : 0, #int(result.revenue),
        'table_data' : table_data,
        'user_id' : my_uid,
    }
    return jsonify(data)

def make_rules(args):
    cpid = args.get("cpid", -1)
    oid = args.get("oid", -1)
    d_oid_name = args.get("d_oid_name", "")
    limit = args.get("limit", -1)
    rules = {}
    rules["cpid"] = int(cpid)
    rules["limit"] = int(limit)
    rules["d_oid_name"] = d_oid_name
    rules["oid"] = int(oid)
    return rules

def load_table_data(uid, time_str, timezone, tags, rules):
    table_tags = {}
    table_items = {}
    table_charts = {}
    table_sorts = {}
    table_sort_format = {}
    table_op = {}
    table_format = {}

    is_campaign_date = False
    if table_config.CAMPAIGN_DATE_TAG in tags:
        is_campaign_date = True

    cp_names = __load_campaign_names(uid)
    for tag in tags:
        class_ins = models.STATIC_RESULT_TYPE_CLASS.get(tag, None)
        if not class_ins:
            continue
        ins = class_ins()
        ins.set_uid(uid)
        ins.parse_time(time_str)
        ins.set_rules(rules)
        ins.set_timezone(timezone)
        ins.set_cpnames(cp_names)
        if is_campaign_date:
            if tag in models.STATIC_ON_PAGING_STATE:
                ins.set_paging((True, [[10,20,50,-1],[10,20,50,'All']]))
            else:
                ins.set_paging((False, []))
        ins.init_data()
        result_list = ins.load_result()
        table_tags[tag] = ins.get_items()
        #table_items[tag] = ins.get_raw_data()
        table_items[tag] = ins.get_kendo_data()
        charts = ins.get_kendo_charts()
        table_charts[tag] = charts
        #table_sorts[tag] = ins.get_sort_default()
        table_sort_format[tag] = ins.get_sort_format()
        table_op[tag] = ins.get_op()
        table_format[tag] = ins.get_column_format()

    table_data = {
        'tags' : tags,
        'items' : table_items,
        'charts' : table_charts,
        #'sorts' : table_sorts,
        #'sort_format' : table_sort_format,
        'op' : table_op,
        'format' : table_format,
    }
    return table_data

def __load_campaign_names(uid):
    res = DBSet.get_db_client().select_all(Campaign, uid=uid)
    names_map = {}
    for obj in res:
        names_map[obj.id] = obj.name
    return names_map

if __name__ == '__main__':
    app.run(settings.bind_ip, settings.bind_port)
