#!/usr/bin/env python
# -*- coding:utf-8 -*-

from mako.template import Template
import time, datetime, ujson

from view_utils import Render, to_links, username2uid
from db_client import Advertiser, Publisher
from utils import TIMEZONE
from models import *
import global_vars
import settings

class ReportView(object):
    def __init__(self, title, tmpl_reader, session_info, url, uid, **custom_tmpl):
        self.title = title
        self.tmpl_reader = tmpl_reader
        self.session_info = session_info
        self.url = url
        self.uid = uid

    def gen_output(self, body_str):
        return body_str

def handle_inner_report(tags, url_name, cookies, args=None, tmpl="reports.tmpl"):
    db_client = global_vars.global_db_set.get_db_client()

    args = args or {}
    timezone = args.get("timezone", TIMEZONE)
    select_username = args.get("username", "")
    username = cookies.get('username')
    user_type = cookies.get('type')
    my_uid = username2uid(username, user_type, db_client)
    select_uid = my_uid

    if select_username != "":
        select_uid = username2uid(select_username, user_type, db_client)
        username = select_username

    #campaigns = DBSet.get_db_client().select_all(Campaign, uid=my_uid)

    start_str, end_str = __get_time_str(args.get("time_str", None))

    if args.get("cpid", None):
        cpid = args["cpid"]
        if cpid == "":
            args["cpid"] = -1

    if args.get("d_oid_name", None):
        d_oid_name = args["d_oid_name"]
        if d_oid_name == "empty":
            args["d_oid_name"] = ""

    d = {
        'tags' : tags,
        'checkbox' : args.get("checkbox", [])
        }
    report_str = render_report_tag(d)

    updatecost_str = render_report_updatecost({})

    d = {
        'date_range_start' : start_str,
        'date_range_end' : end_str,
        #'campaigns' : campaigns,
        'report_str' : report_str,
        'updatecost_str' : updatecost_str,
        'tags' : tags,
        'args' : args,
        'timezone' : timezone,
        'show_title' : 1 if len(tags) > 1 else 0,
        'event_report_list' :  "",
        'event_create_url' : "",
        'event_config_url' : "",
        'user_list' : _get_user_list(my_uid, user_type, db_client),
        'user_id' : select_uid,
    }
    s = render_report_body(d, tmpl)
    return s

def handle_report_grid(tags, chart_tags, url_name, cookies, args=None, tmpl="reports.tmpl"):
    db_client = global_vars.global_db_set.get_db_client()

    args = args or {}
    timezone = args.get("timezone", TIMEZONE)
    select_username = args.get("username", "")
    username = cookies.get('username')
    user_type = cookies.get('type')
    my_uid = username2uid(username, user_type, db_client)
    select_uid = my_uid

    if select_username != "":
        select_uid = username2uid(select_username, user_type, db_client)
        username = select_username

    #campaigns = DBSet.get_db_client().select_all(Campaign, uid=my_uid)

    start_str, end_str = __get_time_str(args.get("time_str", None))
    start_hour = args.get("start_hour", "0")
    end_hour = args.get("end_hour", "23")

    if args.get("cpid", None):
        cpid = args["cpid"]
        if cpid == "":
            args["cpid"] = -1

    if args.get("d_oid_name", None):
        d_oid_name = args["d_oid_name"]
        if d_oid_name == "empty":
            args["d_oid_name"] = ""

    d = {
        'tags' : tags,
        'checkbox' : args.get("checkbox", [])
    }
    report_str = render_report_tag(d)

    #updatecost_str = render_report_updatecost({})

    grids = get_grids(tags, select_uid, args)
    charts = get_charts(chart_tags, select_uid, args)

    d = {
        'grids' : grids,
        'charts' : charts,
        'date_range_start' : start_str,
        'date_range_end' : end_str,
        "start_hour" : start_hour,
        "end_hour" : end_hour,
        'report_str' : report_str,
        'tags' : tags,
        'args' : args,
        'timezone' : timezone,
        'show_title' : 1 if len(tags) > 1 else 0,
        'user_list' : _get_user_list(my_uid, user_type, db_client),
        'user_id' : select_uid,
    }
    s = render_report_body(d, tmpl)
    return s

def get_charts(tags, uid, args):
    ret = []
    for _, tag, _ in tags:
        class_ins = STATIC_RESULT_TYPE_CLASS.get(tag, None)
        if not class_ins:
            continue
        ins = class_ins()
        chart_info = {
            'tag' : "datatable_campaign_hour",
            'name':ins.get_chart_name(args),
            'title': ins.get_chart_title(args),
            'sort': ins.get_chart_sort(args)
        }
        ret.append(chart_info)
    return ret

def get_grids(tags, uid, args):
    ret = []
    for _, tag, _ in tags:
        class_ins = STATIC_RESULT_TYPE_CLASS.get(tag, None)
        if not class_ins:
            continue
        ins = class_ins()
        grid_info = {
            'tag':tag,
            'sort' : ins.get_sort_default(),
            'sort_format' : ins.get_sort_format(),
            'op' : ins.get_op(),
            'col_format' : ins.get_column_format(),
            'fields' : ins.get_fields(),
            'head' : ins.get_items(),
            'filter' : ins.get_filter_items(),
            'bottom_static' : ins.get_bottom_static(),
            'tmp_format' : ins.get_template_format(),
            'toolbar' : ins.get_toolbar(),
            'args' : ins.get_args(uid, args),
            'edit' : ins.get_edit()
        }
        ret.append(ujson.dumps(grid_info))
    return ret

def __get_time_str(time_str, range_days=0):
    start_str = ""
    end_str = ""
    if time_str is None:
        now = datetime.datetime.now()
        start = now - datetime.timedelta(seconds=3600*24*range_days)
        start_str = start.strftime('%m/%d/%Y')
        end_str = now.strftime('%m/%d/%Y')
    else:
        date_list = time_str.split("-")
        start_str = date_list[0].strip()
        end_str = date_list[1].strip()
    return start_str, end_str

def render_report_tag(args):
    report_tmpl = global_vars.tmpl_reader.read_file('report_tag.tmpl')
    report_str = Template(report_tmpl).render(**args)
    return report_str

def render_report_updatecost(args):
    range_hours = []
    for i in xrange(24):
        range_hours.append(i)
    d = {
        'range_hours' : range_hours,
    }
    args.update(d)
    updatecost_tmpl = global_vars.tmpl_reader.read_file('update_cost.tmpl')
    updatecost_str = Template(updatecost_tmpl).render(**args)
    return updatecost_str

def render_report_body(args, tmpl):
    body_tmpl = global_vars.tmpl_reader.read_file(tmpl)
    body_str = Template(body_tmpl).render(**args)
    return body_str

def _get_user_list(uid, user_type, db_client):
    if uid not in settings.admin_white_uid_list:
        return []
    cls = Publisher if int(user_type) == global_vars.PUBLISHER else Advertiser
    users = db_client.select_all(cls)
    user_list = []
    for obj in users:
        user_list.append((int(obj.id), obj.name, uid == int(obj.id)))
    return user_list


