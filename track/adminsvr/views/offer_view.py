#!/usr/bin/env python
# -*-coding:utf-8 -*-
from view import ModelView, Render 
from sqlalchemy import Integer, String, Float
from mako.template import Template
from db_client import User, Offer, LandingPage, Path, SwapRotation, AffiliateNetwork, AdminOffer, AdminOfferPayout, AdminAffiliateNetwork, get_nonprimary_columns,\
        Campaign, SwapRotation, Flow, get_normal_columns
from view import ModelView, Render, BaseColumn, to_links
from utils import get_model_uri, make_url, to_links, check_permission, decode_from_utf8, encode_from_utf8
from flask import redirect, request
from config import country_config, affiliate_config, offer_link_config
from config.permission_config import *
from config.auth_config import SUPER_ADMIN_UID 
from user_db_client import FlowEvent
import time
import ujson
import global_vars
import view_util

_TIMEZONE = -time.timezone / 3600

def objs2dict(objs):
    ret = {}
    for o in objs:
        ret[o.id] = o
    return ret


class OfferView(ModelView):
    p2c = {}
    s2c = {}
    f2c = {}

    def __init__(self, session_info):
        self.table_class = Offer
        self.session_info = session_info
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table

        self.db_client = global_vars.global_db_set.get_db_client()
        self.user_db_client = global_vars.global_db_set.get_user_db_client()
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.args = view_util.get_request_args()
        self.args['uid'] = self.my_uid
        self.tmpl_reader = global_vars.tmpl_reader
        self.editable_fields = ['name', 'cap']
        self.admin_offer = {}
        self.payout_map = {}
        self.is_inner_user = self.check_is_massival_inner_user()
        self.init_admin_offer()

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
            "direct_offer_id" : 0,
            'url' : "",
            "introduction" : "",
        }
        # direct
        offers = self.db_client.iter_all(AdminOffer)
        payouts = self.db_client.iter_all(AdminOfferPayout)
        for p in payouts:
            if p.admin_offer_id not in self.payout_map:
                self.payout_map[p.admin_offer_id] = []
            self.payout_map[p.admin_offer_id].append((p.payout, p.start_time, p.timezone))

        for _id, _list in self.payout_map.items():
            _list.sort(lambda x,y:cmp(x[1],y[1]))

        for o in offers:
            if o.hidden != 0:
                continue
            if o.state != 0:
                continue
            af_name = affiliate_config.AFFILIATE_DICT[o.direct_type]["af_name"]
            if af_name not in self.admin_offer:
                self.admin_offer[af_name] = {}
            ap = self._match_payout(self.payout_map.get(o.id, []), int(time.time())) or o.payout_type
            self.admin_offer[af_name][int(o.id)] = {
                "direct_type":o.direct_type,
                'nick' : o.name,
                'ap' : ap,
                'country' : o.country,
                "direct_offer_id" : o.id,
                "url" : o.url,
                #"introduction" : encode_from_utf8(o.introduction),
                "introduction" : o.introduction
            }


    def get_direct_url(self, args):
        af_id = int(args["direct_type"])
        admin_offer_id = int(args["direct_offer_id"])
        af_info = affiliate_config.AFFILIATE_DICT.get(af_id, None)
        if af_info is None:
            assert af_info is not None
        af_name = af_info["af_name"]
        url= self.admin_offer[af_name][admin_offer_id]["url"]
        return url

    def check_direct(self, args):
        af_id = args["direct_type"]
        af_info = affiliate_config.AFFILIATE_DICT.get(af_id, None)
        if af_info is None:
            args.pop('direct_type')
            args.pop('url')
            return {'direct_type':'miss'}
        af_name = af_info["af_name"]
        if af_id > 0 and not self.admin_offer[af_name].get(int(args['direct_offer_id']), None):
            args.pop('url_direct')
            return {'url_direct':'miss'}
        return {}

    def get_network_id_option(self):
        if self.check_is_massival_inner_user():
            recs = self.db_client.iter_all(AdminAffiliateNetwork, uid=SUPER_ADMIN_UID)
        else:
            recs = self.db_client.iter_all(AffiliateNetwork, uid=self.my_uid)
        return [{"name":rec.name, "id":rec.id} for rec in recs]

    def _check_offer_permission(self, pt, user=None):
        if user is None:
            user = self.db_client.select_one(User, id=self.my_uid)
        return check_permission(PERMISSION_CONFIGURE, user.permission, pt)

    def _do_get_affliate_config(self):
        user = self.db_client.select_one(User, id=self.my_uid)
        af_list = []
        for info in affiliate_config.AFFILIATE_LIST:
            _id, name, op, af_type, pt = info
            if self._check_offer_permission(pt, user):
                af_list.append((_id, name, op, af_type))
        return af_list

    def _get_affiliate_config(self):
        result = {}
        af_list = self._do_get_affliate_config()
        result["list"] = af_list
        #result["link"] = offer_link_config.OfferLink
        result["link"] = self.admin_offer
        return result

    def _filter_editable_fields(self):
        offer = self.db_client.select_one(Offer,id=self.args['id'])
        for col in get_nonprimary_columns(Offer):
            if col.name in self.editable_fields or self.args.get(col.name) is None:
                continue
            self.args[col.name] = getattr(offer, col.name)

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
        model = self.user_db_client.select_one(FlowEvent, uid=self.my_uid)
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
        model = self.user_db_client.select_one(FlowEvent, uid=self.my_uid)
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
            model = FlowEvent()
            model.offers = cap_event
            model.uid = self.my_uid
            return self.user_db_client.add_one(model)
        return False

    def _del_cap_event(self, offer_id):
        model = self.user_db_client.select_one(FlowEvent, uid=self.my_uid)
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
            if self.args['direct_type'] != '0':
                self._filter_editable_fields()
            new_args, error_args = view_util.check_create_args(self.args, self.table_class, self.name2table, self.db_client, check_primary=True)
            if self.args['direct_type'] != '0':
                new_args["url_direct"] = self.get_direct_url(new_args)
            error_args.update(cap_errors)
            if not error_args:
                error_args.update(self.check_direct(new_args))
            has_errors = len(error_args) > 0
            new_args["introduction"] = decode_from_utf8(new_args["introduction"])
            if not has_errors:
                model = Offer(**new_args)
                if self.db_client.do_save(model):
                    kwargs['ret'] = view_util.gen_op_tips("Edit Success!", True)
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
                model = Offer(**new_args)
        else:
            if self.args.get("create"):
                kwargs['ret'] = view_util.gen_op_tips("Create Success!", True)

            model = self.db_client.select_one(Offer, id=int(self.args['id']))
            kwargs["cap"] = self._load_cap_args_from_db(int(self.args['id']))
        return self.output_edit(model, **kwargs)

    def __update_offer(self, args):
        model = Offer(**args)
        tips = ""
        if self.db_client.do_save(model):
            tips = "update patout successed."
        else:
            tips = "update patout faile."
        return tips

    def output_edit(self, model, tips=None, ret="", cap=None):
        cap = cap or {}
        ret_dict = {'tips':{}, 'ret':ret, 'title':"Edit", 'options':{}, 'list_url':global_vars.URL_OFFER_LIST}
        ret_dict.update(cap)
        if tips:
            ret_dict['tips'].update(tips)

        for col in Offer.__table__.columns:
            ret_dict[col.name] = getattr(model, col.name)

        ret_dict["introduction"] = decode_from_utf8(ret_dict["introduction"])
        tmp_path = "offer.tmpl"
        ret_dict['options']['network_id'] = self.get_network_id_option()
        ret_dict['options']['country'] = country_config.COUNTRY_NAME_LIST
        ret_dict['options']['affiliate'] = self._get_affiliate_config()

        if ret_dict["direct_offer_id"] != 0 :
            ret_dict["url_direct"] = model.direct_offer_id
            res, payout = self._check_direct_offer_payout(ret_dict["payout_type"], ret_dict["direct_offer_id"])
            if not res:
                args = {}
                for col in Offer.__table__.columns:
                    args[col.name] = getattr(model, col.name)
                args["payout_type"] = payout
                ret_dict["payout_type"] = payout
                update_tips = self.__update_offer(args)
                ret_dict["tips"]["payout_type"] = view_util.gen_direct_offer_change_tips(payout)

        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})


    def _do_check_network(self):
        error_args = {}
        if self.is_inner_user:
            network_name = {"admin_network_id":AdminAffiliateNetwork}
        else:
            network_name = {"network_id":AffiliateNetwork}

        normal_columns = get_normal_columns(self.table_class)
        for col in normal_columns:
            if col.name in network_name:
                value = self.args.get(col.name, None)
                if value is None:
                    error_args[col.name] = 'miss'
                    continue
                tb_class = network_name[col.name]
                d = {"id":int(value)}
                record = self.db_client.select_one(tb_class, **d)
                if not record:
                    error_args[col.name] = 'select'
        return error_args

    def output_create(self, save=False):
        ret_dict = {'tips':{}, 'ret':"", 'title':"Create", 'options':{}, 'list_url':global_vars.URL_OFFER_LIST}
        if save:
            new_args, error_args = view_util.check_create_args(self.args, self.table_class, self.name2table, self.db_client)
            if int(self.args["direct_type"]) > 0:
                new_args["url_direct"] = self.get_direct_url(self.args)
            error_args.update(self._do_check_network())

            has_errors = len(error_args) > 0
            new_args["introduction"] = decode_from_utf8(new_args["introduction"])
            model = Offer(**new_args)
            if not has_errors:
                if self.db_client.add_one(model):
                    ret_dict['ret'] = view_util.gen_op_tips("Create Success!", True)
                    if self.args['cap'] == "Yes":
                        cap_errors, cap_event, cap_args = self._load_cap_args(model.id)
                        ret_dict.update(cap_args)
                        if not self._add_cap_event(cap_event):
                            ret_dict['ret'] = view_util.gen_op_tips("Add Cap Event Failed!", False)
                    return redirect("%s?id=%d&create=1"%(global_vars.URL_OFFER_EDIT, model.id))
                else:
                    ret_dict['ret'] = view_util.gen_op_tips("Create Failed!", False)
            else:
                for col in Offer.__table__.columns:
                    ret_dict[col.name] = getattr(model, col.name)
                for field in error_args:
                    ret_dict['tips'][field] = view_util.gen_tips()
                ret_dict['ret'] = view_util.gen_op_tips("Create Failed!", False)
        else:
            new_args = {}

        for col in Offer.__table__.columns:
            ret_dict[col.name] = new_args.get(col.name)

        tmp_path = "offer.tmpl"
        ret_dict['options']['network_id'] = self.get_network_id_option()
        ret_dict['options']['country'] = country_config.COUNTRY_NAME_LIST
        ret_dict['options']['affiliate'] = self._get_affiliate_config()
        ret_dict['is_inner_user'] = self.is_inner_user

        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    @staticmethod
    def get_campaign_num(pk_id, offer2flow, flow2camp):
        cids = set()
        for fid in offer2flow.get(pk_id, []):
            cids |= flow2camp.get(fid, set())
        return len(cids)

    @staticmethod
    def get_camp_by_oid(oid, camps, flows, swaps, paths):
        swaps = objs2dict(swaps)
        paths = objs2dict(paths)
        offer2flow = OfferView.init_offer_to_flow(flows, swaps, paths)
        flow2camp = OfferView.init_flow_to_camp(camps)
        cids = set()
        for fid in offer2flow.get(oid, []):
            cids |= flow2camp.get(fid, set())
        return cids

    @staticmethod
    def init_offer_to_flow(flows, swaps, paths):
        offer2flow = {}

        for flow in flows:
            sids = flow.swaps.split(",")
            for sid in sids:
                swap = swaps[int(sid)]
                for pstr in swap.paths.split(","):
                    pid, weight = pstr.split(";")
                    if not weight.isdigit() or int(weight) <= 0:
                        continue
                    path = paths.get(int(pid))
                    if path is None:
                        continue
                    for oid in path.offers.split(","):
                        oid = int(oid)
                        flow_list = offer2flow.get(oid)
                        if flow_list is None:
                            offer2flow[oid] = set([flow.id])
                        else:
                            flow_list.add(flow.id)
        return offer2flow

    @staticmethod
    def init_flow_to_camp(camps):
        flow2camp = {}
        for camp in camps:
            camp_list = flow2camp.get(camp.flow_id)
            if camp_list is None:
                flow2camp[camp.flow_id] = set([camp])
            else:
                camp_list.add(camp)
        return flow2camp

    def output_list(self):
        rows = self.db_client.iter_all(self.table_class, uid=self.my_uid)

        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        filter_cols = ['uid', 'url_direct', 'direct_type']
        name_filter = ['id', 'uid', 'hidden', 'url_direct', 'direct_type', 'direct_offer_id', "introduction"]
        name2title = {'network_id': 'network', 'admin_network_id':'admin network'}
        network_name = ['network_id', 'admin_network_id']
        if self.is_inner_user:
            name_filter.append("network_id")
            filter_cols.append("network_id")
        else:
            name_filter.append("admin_network_id")
            filter_cols.append("admin_network_id")

        field_names = []
        for col in columns:
            if col.name in name_filter:
                continue
            t = "string" if col.is_foreign or isinstance(col.real_column.type, String) or col.name in network_name  else "number"
            col_ret = {'name' :col.name, 'type': t}
            if name2title.get(col.name):
                col_ret['title'] = name2title[col.name]
            field_names.append(col_ret)
        extra_field = [
            {"name":"camp_num", "title":"campaign num", "type":"string"},
        ]
        field_names.extend(extra_field)

        if self.check_is_massival_inner_user():
            networks = self.db_client.iter_all(AdminAffiliateNetwork, uid=SUPER_ADMIN_UID)
        else:
            networks = self.db_client.iter_all(AffiliateNetwork, uid=self.my_uid)
        network_cache = {}


        paths = self.db_client.iter_all(Path, uid=self.my_uid)
        swaps = self.db_client.iter_all(SwapRotation, uid=self.my_uid)
        flows = self.db_client.iter_all(Flow, uid=self.my_uid)
        camps = self.db_client.iter_all(Campaign, uid=self.my_uid)


        paths = objs2dict(paths)
        swaps = objs2dict(swaps)
        offer2flow = self.init_offer_to_flow(flows, swaps, paths)
        flow2camp = self.init_flow_to_camp(camps)

        for i in networks:
            network_cache[i.id] = i.name
        records = []
        for row in rows:
            tmp_records = {}
            pk_id = None
            for column in columns:
                if column.name in filter_cols:
                    continue
                if column.is_primary:
                    pk_id = getattr(row, column.name)

                elif column.is_normal:
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
                            if column.name in network_name:
                                _fid = getattr(row, column.name)
                                v = network_cache[_fid]
                                tmp_records[column.name] = (v)
                            else:
                                tmp_records[column.name] = getattr(row, column.name)

                elif column.is_foreign:
                    if column.name == "network_id":
                        cache = network_cache
                    _fid = getattr(row, column.name)
                    v = cache[_fid]
                    tmp_records[column.name] = (v)
            obj_info = {}
            obj_info['values'] = tmp_records
            obj_info['edit_url'] = make_url(global_vars.URL_OFFER_EDIT, {'url' : request.path, 'id' : pk_id})
            obj_info['query_camp'] = make_url(global_vars.URL_CAMP_LIST, {'url': request.path, 'offer':pk_id})
            obj_info['id'] = pk_id

            n = OfferView.get_campaign_num(pk_id, offer2flow, flow2camp)

            tmp_records['camp_num'] = n

            records.append(obj_info)

        def _cmp(a, b):
            return int(b["id"]) - int(a["id"]) 
        records = sorted(records, _cmp)

        d = {
            'cur_url' : request.path,
            'create_url' : make_url(global_vars.URL_OFFER_CREATE, {'url' : request.path}),
            #'del_url' : self.del_url,
            'field_names' : field_names,
            'records' : records,
            'set_hidden_url' : global_vars.URL_OFFER_SET_HIDDEN,
            'is_inner_user' : self.is_inner_user,
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
            camp = self.db_client.select_one(Offer, id=i)
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
        new_args, error_args = view_util.check_create_args(self.args, self.table_class, self.name2table, self.db_client, is_inner_user=self.is_inner_user)
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


