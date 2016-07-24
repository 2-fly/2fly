#!/usr/bin/env python
# -*-coding:utf-8 -*-

import ujson
import datetime
import view_util
import global_vars

from sqlalchemy import Integer, String, Float
from mako.template import Template
from view import ModelView, Render, BaseColumn, to_links
from utils import get_model_uri, make_url, get_normal_uri, to_links
from flask import redirect, request
from global_vars import global_db_set as DBSet 
from db_client import Offer, User, AdminOffer 
from user_db_client import FlowEvent, AdminFlowEvent

_INVALID_DATA = "#"

_SELECT_OFFER_KEY = "select_offer_id"
_SELECT_TIMEZONE_KEY = "select_offer_timezone"
_SELECT_OFFER_CONV = "select_offer_conv"
_INPUT_OFFER_CONV = "input_offer_conv"

class EventView(ModelView):
    def __init__(self, session_info):
        self.event_tmpl = "flow_event.tmpl"
        self.report_tmpl = "reports.tmpl"
        self.list_tmpl = "flow_event_list.tmpl"
        self.config_tmpl = "flow_event_config.tmpl"
        self.table_class = FlowEvent 
        self.tmpl_reader = global_vars.tmpl_reader
        self.session_info = session_info
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table
        self.user_db_client = DBSet.get_user_db_client()
        self.db_client = DBSet.get_db_client()
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.args = view_util.get_request_args()
        self.offers = []
        self._is_admin = False
        self._init()

    def _init(self):
        self._init_offers()

    def _makeup_args(self):
        args = {}
        args["uid"] = self.my_uid
        args["id"] = self.args.get("id", None)
        try:
            args.update(self._make_profit())
            args.update(self._make_visit())
            args.update(self._make_wanrs())
            args.update(self._make_offers())
        except Exception, ex:
            pass
        return args

    def _make_profit(self):
        args = {}
        select1 = self.args.get("select_profit", "").strip()
        select1 = _INVALID_DATA if select1 == "" else select1
        input1 = self.args.get("input_profit", "").strip()
        input1 = _INVALID_DATA if input1 == "" else float(input1)
        select2 = self.args.get("select_profit2", "").strip()
        select2 = _INVALID_DATA if select2 == "" else select2
        input2 = self.args.get("input_profit2", "").strip()
        input2 = _INVALID_DATA if input2 == "" else float(input2)
        args["profit"] = "%s,%s;%s,%s" % (select1, input1, select2, input2)
        return args 

    def _get_value(self, k):
        v = self.args.get(k, _INVALID_DATA)
        if v == "":
            v = _INVALID_DATA
        return v

    def _check_value_valid(self, *args):
        for k in args:
            if k == _INVALID_DATA:
                return False
        return True

    def _make_offers(self):
        args = {}
        offers = {}
        for k, v in self.args.items():
            if k.find(_SELECT_OFFER_KEY) < 0:
                continue
            idx = int(k[len(_SELECT_OFFER_KEY):])
            s_offer = "%s%s"%(_SELECT_OFFER_KEY, idx)
            s_timezone = "%s%s"%(_SELECT_TIMEZONE_KEY, idx)
            s_conv= "%s%s"%(_SELECT_OFFER_CONV, idx)
            i_conv = "%s%s"%(_INPUT_OFFER_CONV, idx)
            v_offer = self._get_value(s_offer)
            v_timezone = self._get_value(s_timezone)
            v_conv = self._get_value(s_conv)
            i_v_conv = self._get_value(i_conv)
            if self._check_value_valid(v_offer, v_timezone, v_conv, i_v_conv):
                key = "%s,%s,%s,%s" % (v_offer, v_timezone, v_conv, i_v_conv)
                offers[idx] = key
        args["offers"] = "|".join(offers.values())
        return args

    def _make_visit(self):
        visit_list = ['ctr', 'cr', 'roi']
        op_list = ['rate', 'visit']
        return self.__do_make_args(visit_list, op_list)

    def _make_wanrs(self):
        warn_list = ['warn', 'cloak_ts', 'cloak', 'track_domain', 'lander_domain', 'wid_typo', 'wid_digit']
        op_list = ['rate', 'visit', 'warns']
        return self.__do_make_args(warn_list, op_list)

    def __do_make_args(self, key_list, op_list):
        args = {}
        for key in key_list:
            val = ""
            for op in op_list:
                select_key = "select_%s_%s" % (key, op)
                input_key = "input_%s_%s" % (key, op)
                select_val = self.args.get(select_key, "").strip()
                select_val = _INVALID_DATA if select_val == "" else select_val
                input_val = self.args.get(input_key, "").strip()
                input_val = _INVALID_DATA if input_val == "" else input_val 
                if op == "rate" and input_val != _INVALID_DATA:
                    input_val = float(input_val[:-1]) * 0.01
                if val == "":
                    val = "%s,%s" % (select_val,input_val)
                else:
                    val = "%s|%s,%s" % (val,select_val,input_val)
            args[key] = val
        return args

    def _init_offers(self):
        offers = self.db_client.iter_all(Offer, uid=self.my_uid)
        for obj in offers:
            d = {
                "id" : obj.id,
                "name" : obj.name,
            }
            self.offers.append(d)
            
    def _decompose_profit(self, data):
        args = {}
        if data["profit"] == "":
            return args
        array = data["profit"].split(";")
        l1 = array[0].split(",")
        args["select_profit"] = "" if l1[0] == _INVALID_DATA else l1[0]
        args["input_profit"] = "" if l1[1] == _INVALID_DATA else l1[1]

        l2 = array[1].split(",")
        args["select_profit2"] = "" if l2[0] == _INVALID_DATA else l2[0] 
        args["input_profit2"] = "" if l2[1] == _INVALID_DATA else l2[1]
        return args

    def _decompose_visit(self, data):
        visit_list = ['ctr', 'cr', 'roi']
        op_list = ['rate', 'visit']
        return self._do_decompose_args(data, visit_list, op_list)

    def _decompose_warns(self, data):
        warn_list = ['warn', 'cloak_ts', 'cloak', 'track_domain', 'lander_domain', 'wid_typo', 'wid_digit']
        op_list = ['rate', 'visit', 'warns']
        return self._do_decompose_args(data, warn_list, op_list)

    def _do_decompose_args(self, data, key_list, op_list):
        args = {}
        for key in key_list:
            db_value = data[key]
            if db_value == "":
                continue
            array = db_value.split("|")
            for i in xrange(len(op_list)):
                op = op_list[i]
                l = array[i].split(",")
                if len(l) < 2:
                    continue
                select_key = "select_%s_%s" % (key, op)
                input_key = "input_%s_%s" % (key, op)
                args[select_key] = "" if l[0] == _INVALID_DATA else l[0]
                args[input_key] = ""  if l[1] == _INVALID_DATA else l[1]
                if args[input_key] != "":
                    args[input_key] = ("%s"%(float(args[input_key])*100))+"%" if op == "rate" else int(float(args[input_key]))
        return args

    def _decompose_offers(self, data):
        if data["offers"] == "":
            return {}
        offers = data["offers"].split("|")
        args = {}
        for i in xrange(len(offers)):
            o = offers[i]
            idx = i + 1
            v = o.split(",")
            s_offer = int(v[0])
            s_timezone = int(v[1])
            s_conv = v[2]
            i_conv = int(v[3])
            k_offer = "%s%s" % (_SELECT_OFFER_KEY, idx)
            k_timezone = "%s%s" % (_SELECT_TIMEZONE_KEY, idx)
            k_conv = "%s%s" % (_SELECT_OFFER_CONV, idx)
            k_i_conv = "%s%s" % (_INPUT_OFFER_CONV, idx)
            args[k_offer] = s_offer
            args[k_timezone] = s_timezone
            args[k_conv] = s_conv
            args[k_i_conv] = i_conv
        args["offers_len"] = len(offers)
        return args;

    def _decompose_args(self, data):
        args = {}
        args["id"] = int(data["id"])
        args.update(self._decompose_profit(data))
        args.update(self._decompose_visit(data))
        args.update(self._decompose_warns(data))
        args.update(self._decompose_offers(data))
        return args
        
    def get_urls(self):
        ret_dict = {
            "list_url" : global_vars.URL_EVENTS_LIST,
            "report_url" : global_vars.URL_EVENTS_REPORT,
            "create_url" : global_vars.URL_EVENTS_CREATE,
            "edit_url" : global_vars.URL_EVENTS_EDIT,
            "config_url" : global_vars.URL_EVENTS_CONFIG,
        }
        return ret_dict

    def output_event_view(self, tips=None, ret=None):
        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        ret_dict = {
            "tips" : tips or {},
            "result" : ret or "",
            "offers" : self.offers,
            }
        ret_dict.update(self.get_urls())

        uid = self.my_uid if not self._is_admin else 1
        objs = self.user_db_client.select_all(self.table_class, uid=uid)
        data = {}
        if len(objs) > 0:
            model = objs[0]
            data = {}
            for col in self.table_class.__table__.columns:
                data[col.name] = getattr(model, col.name)
            ret_dict.update({"data":self._decompose_args(data)})
        else:
            for col in self.table_class.__table__.columns:
                data[col.name] = "" 
            ret_dict.update({"data":data})

        body_tmpl = self.tmpl_reader.read_file(self.event_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})
        
    def output_event_create(self, create=True):
        kwargs = {}
        if not create and len(self.args) > 0:
            _args = self._makeup_args()
            is_check_primary = False
            if self.args.get("id", None) is not None:
                is_check_primary = True
            new_args, error_args = view_util.check_create_args(_args, self.table_class, self.name2table, self.user_db_client, check_primary=is_check_primary)
            has_errors = len(error_args) > 0
            new_args["uid"] = new_args["uid"] if not self._is_admin else 1

            model = self.table_class(**new_args)
            if not has_errors:
                if self.user_db_client.do_save(model):
                    kwargs['ret'] = view_util.gen_op_tips("Edit Success!", True)
                else:
                    kwargs['ret'] = view_util.gen_op_tips("Edit Failed!", False)
            else:
                kwargs['tips'] = {}
                for field in error_args:
                    kwargs['tips'][field] = view_util.gen_tips()
                kwargs['ret'] = view_util.gen_op_tips("Edit Failed!", False)

        #return redirect(get_model_uri(FlowEvent, "list"))
        return self.output_event_view(**kwargs)
    
    def output_event_report(self):
        render = Render('Mobitx Report %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        ret_dict = self.get_urls()

        body_tmpl = self.tmpl_reader.read_file(self.report_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def _get_all_flow_events(self):
        event_list = []
        events = self.user_db_client.select_all(self.table_class, uid=self.my_uid)
        return event_list

    def output_event_list(self):
        render = Render('Mobitx Report %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        event_list = self._get_all_flow_events()
        ret_dict = {
            "records" : event_list,
        }
        ret_dict.update(self.get_urls())
        body_tmpl = self.tmpl_reader.read_file(self.list_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def __check_config_args(self):
        if len(self.args) > 0:
            return True
        return False

    def output_event_config(self):
        email_str = ""
        tips = None
        try:
            uid = self.my_uid
            userObj = self.db_client.select_one(User, id=uid)
            if userObj:
                if self.__check_config_args():
                    email_str = self.args.get("email_list", "")
                    userObj.event_email= email_str
                    self.db_client.do_save(userObj)
                else:
                    email_str = userObj.event_email
        except Exception, ex:
            print ex

        render = Render('Mobitx Config %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        ret_dict = {
            "email_list" : email_str,
            "tips" : tips,
        }
        ret_dict.update(self.get_urls())
        body_tmpl = self.tmpl_reader.read_file(self.config_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})


class AdminEventView(EventView):
    def __init__(self, session_info):
        super(AdminEventView, self).__init__(session_info)
        self.event_tmpl = "admin_flow_event.tmpl"
        self.report_tmpl = "reports.tmpl"
        self.table_class = AdminFlowEvent 
        self._is_admin = True

    def _init_offers(self):
        offers = self.db_client.iter_all(AdminOffer)
        for obj in offers:
            d = {
                "id" : obj.id,
                "name" : obj.name,
            }
            self.offers.append(d)

    def get_urls(self):
        urls = {
            "create_url" : global_vars.URL_RELATIVE_EVENTS_CREATE,
            "edit_url" : global_vars.URL_RELATIVE_EVENTS_EDIT,
            "report_url" : global_vars.URL_RELATIVE_EVENTS_REPORT,
            "config_url" : global_vars.URL_EVENTS_CONFIG,
        }
        return urls
