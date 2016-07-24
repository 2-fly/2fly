#!/usr/bin/env python
# -*-coding:utf-8 -*-
from view import ModelView, Render
from sqlalchemy import Integer, String, Float
from mako.template import Template
from db_client import AdminOffer, AdminOfferPayout, Offer
from user_db_client import AdminFlowEvent
from view import ModelView, Render, BaseColumn, to_links
from utils import get_model_uri, make_url, to_links, decode_from_utf8, encode_from_utf8
from flask import redirect, request
from config import country_config, affiliate_config
from global_vars import global_db_set as DBSet
import ujson
import time
import datetime
import global_vars
import view_util

_TIMEZONE = 8
class AdminOfferView(ModelView):
    def __init__(self, session_info):
        self.tmpl = "admin_offer.tmpl"
        self.table_class = AdminOffer
        self.session_info = session_info
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table

        self.db_client = DBSet.get_db_client()
        self.user_db_client = DBSet.get_user_db_client()
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.args = view_util.get_request_args()
        self.args['uid'] = self.my_uid
        self.tmpl_reader = global_vars.tmpl_reader
        self.admin_offer = {}
        self.payout_map = {}
        self.init_admin_offer()

    def init_admin_offer(self):
        # not direct
        afObj = affiliate_config.AFFILIATE_DICT[0]
        af_name = afObj["af_name"]
        self.admin_offer[af_name] = {}
        self.admin_offer[af_name]["empty"] = {
            "direct_type": afObj["direct_type"],
            'nick' : "",
            'ap' : 0,
            'country' : "",
        }
        # direct
        offers = self.db_client.iter_all(AdminOffer)#, uid=self.my_uid)
        for o in offers:
            if o.hidden != 0:
                continue
            af_name = affiliate_config.AFFILIATE_DICT[o.direct_type]["af_name"]
            if af_name not in self.admin_offer:
                self.admin_offer[af_name] = {}
            self.admin_offer[af_name][o.url] = {
                "direct_type":o.direct_type,
                'nick' : o.name,
                'ap' : o.payout_type,
                'country' : o.country,
            }


    def check_direct(self, args):
        af_id = args["direct_type"]
        af_info = affiliate_config.AFFILIATE_DICT.get(af_id, None)
        if af_info is None:
            args.pop('direct_type')
            args.pop('url')
            return {'direct_type':'miss'}
        return {}
        af_name = af_info["af_name"]
        if not self.admin_offer[af_name].get(args['url'], None):
            args.pop('url')
            return {'url':'miss'}
        return {}

    def _do_get_affiliate_config(self):
        af_list = []
        for info in affiliate_config.AFFILIATE_LIST:
            _id, name, op, af_type, pt = info
            af_list.append((_id,name,op,af_type))
        return af_list

    def _get_affiliate_config(self):
        result = {}
        #result["list"] = affiliate_config.AFFILIATE_LIST
        result["list"] = self._do_get_affiliate_config()
        #result["link"] = offer_link_config.OfferLink
        result["link"] = self.admin_offer
        return result

    def _match_payout(self, payout_list, ts):
        last_payout = None
        for i in xrange(len(payout_list)):
            payout, start_ts, timezone = payout_list[i]
            diff_ts = (_TIMEZONE - timezone) * 3600
            if ts >= start_ts + diff_ts:
                last_payout = payout
        return last_payout

    def _check_direct_offer_payout(self, payout, direct_offer_id):
        payout_list = self.payout_map.get(direct_offer_id, [])
        new_payout = self._match_payout(payout_list, int(time.time())) or payout
        return new_payout == payout, new_payout

    def _init_payout_map(self, admin_offer_id):
        self.payout_map = {}
        payouts = self.db_client.iter_all(AdminOfferPayout, admin_offer_id=admin_offer_id)
        for p in payouts:
            if p.admin_offer_id not in self.payout_map:
                self.payout_map[p.admin_offer_id] = []
            self.payout_map[p.admin_offer_id].append((p.payout, p.start_time, p.timezone))

    def _update_related_offers(self, admin_offer_id, args):
        # direct
        self._init_payout_map(admin_offer_id)
        for _id, _list in self.payout_map.items():
            _list.sort(lambda x,y:cmp(x[1],y[1]))

        res, payout = self._check_direct_offer_payout(args["payout_type"], admin_offer_id)
        #update
        offers = self.db_client.iter_all(Offer, direct_offer_id=admin_offer_id)
        for o in offers:
            _args = {}
            for col in Offer.__table__.columns:
                _args[col.name] = getattr(o, col.name)
            _args["payout_type"] = payout
            country = args.get("country", None)
            if country is not None:
                _args["country"] = country
            url = args.get("url", None)
            if url is not None:
                _args["url_direct"] = url
            introduction = args.get("introduction", None)
            if introduction is not None:
                _args["introduction"] = introduction
            model = Offer(**_args)
            self.db_client.do_save(model)

    def edit(self, save=False):
        kwargs = {}
        if save:
            cap_errors = {}
            cap_event = ""
            if self.args['cap'] == "Yes":
                cap_errors, cap_event, cap_args = self._load_cap_args(self.args['id'])
                kwargs["cap"] = cap_args
                kwargs["cap"]["cap"] = "Yes"
            else:
                kwargs["cap"] = {"cap":"No"}
            new_args, error_args = view_util.check_create_args(self.args, self.table_class, self.name2table, self.db_client, check_primary=True)
            if not error_args:
                error_args.update(self.check_direct(new_args))
            has_errors = len(error_args) > 0
            if not has_errors:
                model = AdminOffer(**new_args)

                if self.db_client.do_save(model):
                    kwargs['ret'] = view_util.gen_op_tips("Edit Success!", True)
                    self._update_related_offers(new_args["id"], new_args)
                    if self.args['cap'] == "Yes":
                        if not self._add_cap_event(cap_event):
                            kwargs['ret'] = view_util.gen_op_tips("Add Cap Event Failed!", False)
                    else:
                        if not self._del_cap_event(model.id):
                            kwargs['ret'] = view_util.gen_op_tips("Delete Cap Event Failed!", False)
                else:
                    kwargs['ret'] = view_util.gen_op_tips("Edit Failed!", False)
            else:
                kwargs['tips'] = {}
                for field in error_args:
                    kwargs['tips'][field] = view_util.gen_tips()
                model = AdminOffer(**new_args)
        else:
            if self.args.get("create"):
                kwargs['ret'] = view_util.gen_op_tips("Create Success!", True)

            model = self.db_client.select_one(AdminOffer, id=int(self.args['id']))
            kwargs["cap"] = self._load_cap_args_from_db(int(self.args['id']))

        return self.output_edit(model, **kwargs)

    def _output_current_payout(self, payout, offer_id):
        self._init_payout_map(offer_id)
        res, current_payout = self._check_direct_offer_payout(payout, offer_id)
        if payout != current_payout:
            return "current payout is %s" % current_payout
        return ""

    def output_edit(self, model, tips=None, ret="", cap=None):
        cap = cap or {}
        tips = tips or {}
        ret_dict = {'tips':{}, 'ret':ret, 'title':"Edit", 'options':{}, 'list_url':global_vars.URL_ADMIN_OFFER_LIST}
        for col in AdminOffer.__table__.columns:
            ret_dict[col.name] = getattr(model, col.name)

        ret_dict['tips'].update(tips)
        ret_dict.update(cap)

        ret_dict['tips']['current_payout_type'] = self._output_current_payout(model.payout_type, model.id)

        ret_dict["introduction"] = decode_from_utf8(ret_dict["introduction"])

        ret_dict['options']['country'] = country_config.COUNTRY_NAME_LIST
        ret_dict['options']['affiliate'] = self._get_affiliate_config()

        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})


    def output_create(self, save=False):
        ret_dict = {'tips':{}, 'ret':"", 'title':"Create", 'options':{}, 'list_url':global_vars.URL_ADMIN_OFFER_LIST}
        if save:
            new_args, error_args = view_util.check_create_args(self.args, self.table_class, self.name2table, self.db_client)
            has_errors = len(error_args) > 0
            model = AdminOffer(**new_args)
            if not has_errors:
                if self.db_client.add_one(model):
                    ret_dict['ret'] = view_util.gen_op_tips("Create Success!", True)
                    if self.args['cap'] == "Yes":
                        cap_errors, cap_event, cap_args = self._load_cap_args(model.id)
                        ret_dict.update(cap_args)
                        if not self._add_cap_event(cap_event):
                            ret_dict['ret'] = view_util.gen_op_tips("Add Cap Event Failed!", False)
                    return redirect("%s?id=%d&create=1"%(global_vars.URL_ADMIN_OFFER_EDIT, model.id))
                else:
                    ret_dict['ret'] = view_util.gen_op_tips("Create Failed!", False)
            else:
                for col in AdminOffer.__table__.columns:
                    ret_dict[col.name] = getattr(model, col.name)
                for field in error_args:
                    ret_dict['tips'][field] = view_util.gen_tips()
                ret_dict['ret'] = view_util.gen_op_tips("Create Failed!", False)

        for col in AdminOffer.__table__.columns:
            ret_dict[col.name] = None

        ret_dict['options']['country'] = country_config.COUNTRY_NAME_LIST
        ret_dict['options']['affiliate'] = self._get_affiliate_config()

        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def output_list(self):
        rows = self.db_client.iter_all(self.table_class)

        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        filter_cols = ['uid']
        name_filter = ['uid', 'hidden', 'introduction']

        field_names = []
        for col in columns:
            if col.name in name_filter:
                continue
            t = "string" if isinstance(col.real_column.type, String) else "number"
            if col.is_normal:
                field_names.append({
                    'name' :col.name,
                    'is_normal' : True,
                    'type': t,
                })

            if col.is_foreign and col.name not in filter_cols:
                field_names.append({
                    'name' : col.name,
                    'is_normal' : False,
                    'type': "string",
                })

        records = []
        for row in rows:
            tmp_records = {}
            pk_id = None
            for column in columns:
                if column.is_primary:
                    pk_id = getattr(row, column.name)

                if column.is_normal:
                    if column.is_multi:
                        vs = getattr(row, column.name)
                        ids = [int(_id) for _id in vs.split(',')] if vs else []
                        options = self.get_multi_options(column.multi_table, column.multi_id, 'name')
                        ret_names = []
                        for _id in ids:
                            ret_names.append(options.get(_id, 'unknown'))
                        tmp_records[column.name] = ','.join(ret_names)
                    else:
                        if column.is_textarea:
                            tmp_records[column.name] = ('[CONTENT CANNOT READ]')
                        else:
                            tmp_records[column.name] = (getattr(row, column.name))

                if column.is_foreign and column.name not in filter_cols:
                    source_col = column.foreign_source_key

                    _fid = getattr(row, column.name)
                    v = self.get_foreign_key_field_data(source_col, 'name', col.name, _fid)

                    tmp_records[column.name] = (v)

            obj_info = {}
            obj_info['values'] = tmp_records
            obj_info['edit_url'] = make_url(global_vars.URL_ADMIN_OFFER_EDIT, {'url' : request.path, 'id' : pk_id})
            obj_info['id'] = pk_id
            records.append(obj_info)

        def _cmp(a, b):
            return int(b["id"]) - int(a["id"])
        records = sorted(records, _cmp)

        d = {
            'cur_url' : request.path,
            'create_url' : make_url(global_vars.URL_ADMIN_OFFER_CREATE, {'url' : request.path}),
            #'del_url' : self.del_url,
            'field_names' : field_names,
            'records' : records,
            'set_hidden_url' : global_vars.URL_ADMIN_OFFER_SET_HIDDEN,
        }

        title = 'Massival %s List'%self.table_class.__name__
        render = Render(title, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file('toolbar_model_list.tmpl')
        body_str = Template(body_tmpl).render(**d)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def set_hidden(self):
        ids = self.args['ids']
        back = self.args['back']
        t = int(self.args['type'])

        assert t in [1, 0]

        ids = [int(i) for i in ids.split(",")]
        for i in ids:
            camp = self.db_client.select_one(AdminOffer, id=i)
            if camp:
                camp.hidden = t
                self.db_client.do_save(camp)

        return redirect(back)

    def get_foreign_key_field_data(self, foreign_source_key, tag_name, key_name, fid):
        table_name = foreign_source_key.target_fullname.split('.')[0]
        pk_name = foreign_source_key.target_fullname.split('.')[1]
        tb_class = self.name2table.get(table_name)
        rec = self.db_client.select_one(tb_class, id=fid, uid=self.my_uid)
        return getattr(rec, tag_name)


    def create_return_json(self):
        new_args, error_args = view_util.check_create_args(self.args, self.table_class, self.name2table, self.db_client)
        has_errors = len(error_args) > 0
        err_msg = ''
        if not has_errors:
            model = self.table_class(**new_args)
            try:
                self.db_client.add_one(model)
                json_dict = {'id':model.id, 'name':model.name, 'ret':'suc'}
            except Exception, ex:
                json_dict = {'ret':'fail', 'msg': ex}
        else:
            error_args.update({'ret':'fail'})
            json_dict = error_args
        return ujson.dumps(json_dict)

    def _load_cap_args(self, offer_id):
        uid = self.my_uid
        timezone = self.args.pop("timezone", 8)
        conv_op = self.args.pop("conv_op", "")
        conv = self.args.pop("conv", "")
        errors = {}
        if conv_op == "":
            errors.update({"conv_op":"miss"})
        if conv == "":
            errors.update({"conv":"miss"})
        key = ""
        args = {}
        if len(errors) == 0:
            key = "%s,%s,%s,%s" % (offer_id, timezone, conv_op, conv)
            args = {
                "timezone" : timezone,
                "conv_op" : conv_op,
                "conv" : conv
            }
        return errors, key, args

    def _load_cap_args_from_db(self, offer_id):
        #model = self.user_db_client.select_one(AdminFlowEvent, uid=self.my_uid)
        model = self.user_db_client.select_one(AdminFlowEvent, uid=1)
        args = {
                "cap" : "No"
            }
        if model:
            offer_list = model.offers.split("|")
            for info in offer_list:
                parts = info.split(",")
                if len(parts) != 4:
                    continue
                if offer_id == int(parts[0]):
                    args = {
                        "timezone" : int(parts[1]),
                        "conv_op" : parts[2],
                        "conv" : parts[3],
                        "cap" : "Yes",
                    }
                    break
        return args

    def _add_cap_event(self, cap_event):
        #model = self.user_db_client.select_one(AdminFlowEvent, uid=self.my_uid)
        model = self.user_db_client.select_one(AdminFlowEvent, uid=1)
        if model:
            if model.offers == "":
                model.offers = cap_event
            else:
                offer_result = model.offers.split("|")
                cap_parts = cap_event.split(",")
                for idx in xrange(len(offer_result)):
                    info = offer_result[idx]
                    parts = info.split(",")
                    if len(parts) != 4:
                        continue
                    if parts[0] == cap_parts[0]:
                        offer_result[idx] = cap_event
                        break
                else:
                    offer_result.append(cap_event)
                model.offers = "|".join(offer_result)
            return self.user_db_client.do_save(model)
        else:
            model = AdminFlowEvent()
            model.offers = cap_event
            #model.uid = self.my_uid
            model.uid = 1
            return self.user_db_client.add_one(model)
        return False

    def _del_cap_event(self, offer_id):
        #model = self.user_db_client.select_one(AdminFlowEvent, uid=self.my_uid)
        model = self.user_db_client.select_one(AdminFlowEvent, uid=1)
        if model:
            offer_list = model.offers.split("|")
            result = []
            for info in offer_list:
                parts = info.split(",")
                if len(parts) != 4:
                    continue
                if int(parts[0]) != int(offer_id):
                    result.append(info)
            model.offers = "|".join(result)
            return self.user_db_client.do_save(model)
        return True


def ts_to_date(ts):
    return datetime.datetime.fromtimestamp(ts)

def selectAdminOffer(admin_offer_id):
    objs = DBSet.get_db_client().iter_all(AdminOfferPayout, admin_offer_id=admin_offer_id)
    data = []
    for obj in objs:
        data.append([obj.start_time, obj.timezone, obj.payout])
    data.sort(lambda x,y:cmp(x[0],y[0]), reverse=True)
    cnt = 0
    result = []
    for info in data:
        dt = ts_to_date(info[0])
        datetime_str = dt.strftime('%Y-%m-%d %H:00')
        info[0] = datetime_str
        result.append(info)
        cnt += 1
        if cnt >= 5:
            break
    return result

def updateAdminOfferPayout(session_info, admin_offer_id, start_time, timezone, payout):
    uid = view_util.username2uid(session_info['username'], DBSet.get_db_client())
    new_args = {
        "uid" : uid,
        "admin_offer_id" : admin_offer_id,
        "start_time" : start_time,
        "timezone" : timezone,
        "payout" : payout
    }
    model = AdminOfferPayout(**new_args)
    return DBSet.get_db_client().add_one(model)
