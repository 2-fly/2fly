#!/usr/bin/env python
# -*-coding:utf-8 -*-
from sqlalchemy import Integer, String, Float
from config import rule_config,country_config
from view import ModelView, Render, BaseColumn
from flask import redirect, request
from db_client import get_normal_columns, get_primary_keys, get_foreign_source_keys, get_foreign_keys, \
        get_nonprimary_columns, get_columns
from utils import get_model_uri, make_url, to_links
from commlib.utils.httputils import is_subdomain
from commlib.db.redis_helper import RedisHashTable2
from commlib.db.db_tabledef import virus_domains_key, virusdomains_admin_table
from mako.template import Template
from db_client import Offer, LandingPage, Path, SwapRotation, AffiliateNetwork, Campaign, User, Flow, TrafficSource, CampaignCost, AdminTrafficSource, SwitchPath
from global_vars import global_db_set as DBSet
from offer_view import OfferView
from config.permission_config import PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_SWITCH_PATH
import copy
import global_vars
import view_util
import ujson
import time
import settings
import datetime

CREATE_TMPL_PATH = 'campaign.tmpl'
EDIT_TMPL_PATH = 'campaign.tmpl'

TYPE_LANDER = 1
TYPE_OFFER = 2
_TIMEZONE = 8

def gen_update_campaign_cost_tips(cost):
    return '<span class="label label-success" style="margin-left:20px">cost has changed to %s </span>' % (cost)

def gen_op_tips(tips, success=False):
    if not success:
        return '''<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></div>'''%tips
    else:
        return '''<div class="alert alert-success"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></div>'''%tips

def gen_tips(msg = None):
    if not msg:
        msg = "field is error!"
    if type(msg) == dict:
        msg = ujson.dumps(msg)
    else:
        msg = '''<div class="control-group">
            <label class="control-label"></label>
            <div class="controls">
                <span class="label label-important">%s</span>
            </div>
        </div>'''%msg
    return msg

def model_to_dict(records):
    ret = {}
    for rec in records:
        ret[rec.id] = rec
    return ret

class CampaignView(ModelView):
    def __init__(self, session_info):
        self.table_class = Campaign
        self.session_info = session_info
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table

        self.db_client = DBSet.get_db_client()
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.args = view_util.get_request_args()
        self.args['uid'] = self.my_uid
        self.tmpl_reader = global_vars.tmpl_reader
        self.list_url = get_model_uri(self.table_class, 'list')
        self.is_inner_user = self.check_is_massival_inner_user()

        self.get_options = {
        }

    def init_campaign_cost(self, cpid):
        self._campaign_cost_list= []
        objs = self.db_client.iter_all(CampaignCost, uid=self.my_uid, cpid=cpid)
        for o in objs:
            l = [o.start_time, o.timezone, o.cost]
            self._campaign_cost_list.append(l)
        self._campaign_cost_list.sort(lambda x,y:cmp(x[0], y[0]))

    def save_flow(self, flow):
        pass


    def do_save(self, **kargs):
        err_msg = ""
        campaign_name = kargs['name']

        self.save_flow(kargs['flow_id'])

        new_kargs = view_util.filter_model_key(self.table_class, kargs)
        model = self.table_class(**new_kargs)
        try:
            assert self.db_client.do_save(model)
        except Exception, ex:
            return ex
        return ''

    def add_one(self, **kargs):
        err_msg = ""
        campaign_name = kargs['name']

        self.save_flow(kargs['flow_id'])

        new_kargs = view_util.filter_model_key(self.table_class, kargs)
        model = self.table_class(**new_kargs)
        try:
            assert self.db_client.add_one(model)
        except Exception, ex:
            return ex
        return model.id

    def check_swap_id(self):
        lander = []
        offer = []
        error_args = {}
        new_args = {}

        try:
            swap_id = int(self.args['swap_id'])
            if swap_id != -1 and not self.db_client.select_one(SwapRotation, id=int(swap_id)):
                error_args['swap_id'] = "miss"
                return new_args, error_args
            if swap_id == -1 and not self.args['swap_name']:
                error_args['swap_id'] = "miss"
                return new_args, error_args
            else:
                new_args['swap_name'] = self.args['swap_name']
            paths = ujson.loads(self.args.get('paths', ""))
        except Exception, ex:
            error_args['swap_id'] = "miss"
            return new_args, error_args
        paths = [path for path in paths if path]

        for path in paths:
            path_id = path['path_id'] if not path['is_new'] else 0
            if path_id and not self.db_client.select_one(Path, id=path_id):
                error_args['swap_id'] = "miss"
                return new_args, error_args
            try:
                for v in path['lander']:
                    if not self.db_client.select_one(LandingPage, id=int(v)):
                        error_args['swap_id'] = "miss"
                        return new_args, error_args
                for v in path['offer']:
                    if not self.db_client.select_one(Offer, id=int(v)):
                        error_args['swap_id'] = "miss"
                        return new_args, error_args
            except Exception, ex:
                error_args['swap_id'] = "miss"
                return new_args, error_args
        new_args['paths'] = paths
        new_args['swap_id'] = swap_id
        return new_args, error_args

    def check_rules(self, rules):
        for r in rules:
            cdts = ujson.loads(r['condition'])
            ms = r["match_swap"]
            r['condition'] = cdts
            if ms['swap_id'] != -1 and not self.db_client.select_one(SwapRotation, id=ms['swap_id']):
                return False
            for path in ms['paths']:
                path_id = path['path_id'] if not path['is_new'] else 0
                if path_id and not self.db_client.select_one(Path, id=path_id):
                    return False
                try:
                    for v in path['lander']:
                        if not self.db_client.select_one(LandingPage, id=int(v)):
                            return False
                    for v in path['offer']:
                        if not self.db_client.select_one(Offer, id=int(v)):
                            return False
                except Exception, ex:
                    return False
            for cdt in cdts:
                for rule_id in cdt['rules']:
                    if not rule_config.rule.get(rule_id):
                        return False
        return True

    def check_path(self, p):
        for l in p['lander']:
            assert self.db_client.select_one(LandingPage, id=l)
        for o in p['offer']:
            assert self.db_client.select_one(Offer, id=o)

    def check_flow(self, flow):
        if flow.get("id"):
           assert self.db_client.select_one(Flow, id=flow['id'])
           assert self.db_client.select_one(SwapRotation, id=flow['default_swap']['id'])
           for r in flow['rules']:
               if r['match_swap'].get('id'):
                   assert self.db_client.select_one(SwapRotation, id=r['match_swap']['id'])
        for p in flow['default_swap']['paths']:
            self.check_path(p)

        for r in flow['rules']:
            for p in r['match_swap']['paths']:
                self.check_path(p)
        return True

    def check_flow_id(self, flow):
        swaps = flow.swaps.split(",") if flow.swaps else []
        for swap_id in swaps:
            swap = self.db_client.select_one(SwapRotation, id=int(swap_id))
            if not swap:
                continue
            paths = swap.paths.split(",") if swap.paths else []
            for path_id in paths:
                path_id, weight = path_id.split(";")
                if not int(weight):
                    continue
                path = self.db_client.select_one(Path, id=int(path_id))
                if not path:
                    continue
                offers = path.offers.split(",") if path.offers else []
                for offer_id in offers:
                    offer = self.db_client.select_one(Offer, id=int(offer_id))
                    if not offer:
                        continue
                    if offer.direct_type == 1 and not int(self.args.get("ck_cloak", 0)):
                        return False, {"ck_cloak":"must turn on ck_cloak"}
        return True, ""

    def check_create_args(self, check_primary=False):
        normal_columns = get_normal_columns(self.table_class)
        foreign_columns = get_foreign_keys(self.table_class)
        foreign_source_columns = get_foreign_source_keys(self.table_class)
        primary_columns = get_primary_keys(self.table_class) if check_primary else []

        if self.is_inner_user:
            ts_name = {'admin_source_id' : AdminTrafficSource,}
        else:
            ts_name = {'source_id' : TrafficSource,}

        error_args = {}
        new_args = {}
        for col in normal_columns:
            value = self.args.get(col.name)

            if value is None:
                if col.name in view_util.nullable_field:
                    continue
                else:
                    error_args[col.name] = 'miss'
                    continue
            if type(col.type) == String:
                if col.default is None and not value:
                    error_args[col.name] = 'miss'
                new_args[col.name] = value.strip().encode("utf8")
            elif type(col.type) == Integer:
                try:
                    new_args[col.name] = int(value)
                except ValueError:
                    error_args[col.name] = 'select'
            elif type(col.type) == Float:
                try:
                    new_args[col.name] = float(value)
                except ValueError:
                    error_args[col.name] = 'select'
            else:
                raise Exception('unknown field type: %s'%type(col.type))
            if col.name == 'name':
                names = value.split("-")
                if len(names) < 3 or not names[2]:
                    error_args[col.name] = 'miss'
            if col.name in ts_name:
                tb_class = ts_name[col.name]
                d = {"id":int(value)}
                record = self.db_client.select_one(tb_class, **d)
                if not record:
                    error_args[col.name] = 'select'

        filter_cols = ['swap_id']

        for i in xrange(len(foreign_columns)):
            col = foreign_columns[i]
            value = self.args.get(col.name)
            if col.name in filter_cols:
                continue
            if value is None :
                error_args[col.name] = 'miss'
                continue
            try:
                new_args[col.name] = int(value)
            except ValueError:
                error_args[col.name] = 'select'
                continue

            new_value = int(value)
            source_col = foreign_source_columns[i]
            table_name = source_col.target_fullname.split('.')[0]
            field_name = source_col.target_fullname.split('.')[1]
            d = {field_name : new_value}
            tb_class = self.name2table.get(table_name)
            record = self.db_client.select_one(tb_class, **d)
            if not record:
                error_args[col.name] = 'select'
            if hasattr(self, "check_" + col.name):
                check_handler = getattr(self, "check_" + col.name)
                ret, err = check_handler(record)
                if not ret:
                    error_args.update(err)


        for col in primary_columns:
            value = self.args.get(col.name)
            if value is None:
                error_args[col.name] = 'miss'
                continue

            try:
                new_args[col.name] = int(value)
            except ValueError:
                error_args[col.name] = 'select'
                continue

            new_value = int(value)
            field_name = col.name
            d = {field_name : new_value}
            records = self.db_client.select_all(self.table_class, **d)
            if not records:
                error_args[col.name] = 'select'
        dist_error = self.check_lander_domains(new_args)
        if dist_error:
            error_args['lander_domains_dist'] = dist_error
        return new_args, error_args

    def check_lander_domains(self, new_args):
        self.redis_cli = RedisHashTable2(host=settings.redis_host, port=settings.redis_port)
        dist = new_args.get("lander_domains_dist")
        if not dist:
            return {}
        user = self.db_client.select_one(User, id=self.my_uid)
        lander_domains = [i.split(";")[0] for i in user.lander_domains.split(",")]
        ret = {}
        for domain in dist.split(","):
            domain, hidden = domain.split(";")
            hidden = int(hidden)
            msg = ""
            f = False
            for lander_domain in lander_domains:
                is_sub = is_subdomain(domain, [lander_domain])
                if is_sub and not hidden:
                    url_ret = self.redis_cli.get_one(virusdomains_admin_table, domain)
                    if url_ret:
                        url_ret = ujson.loads(url_ret)
                        if url_ret['positives'] > 0:
                            detail = '(%d/%d)'%(url_ret['positives'], url_ret['total'])
                            status = 'bad'
                            msg += "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp".join([status + detail, url_ret['scan_date']])
                    f = True
                    break
                elif is_sub and hidden:
                    f = True
                    break
            if not f:
                msg += "not found in lander domains"
            if msg:
                ret[domain] = msg
        return ret

    def init_static_data(self, op_tips, create=True):
        ret_dict = {}
        ret_dict['options'] = {}
        ret_dict['tips'] = {}
        ret_dict['list_url'] = self.list_url
        ret_dict['campaign_url'] = global_vars.URL_CAMP_CREATE
        ret_dict['op_tips'] = op_tips
        ret_dict['title'] = 'Edit' if not create else 'Create'
        ret_dict['rule_config'] = rule_config
        ret_dict['sec_cate_url'] = global_vars.URL_CAMP_RULE_SEC_CATE
        ret_dict['save_flow_url'] = global_vars.URL_FLOW_SAVE
        ret_dict['get_flow_url'] = global_vars.URL_FLOW_GET
        ret_dict['get_source_url'] = global_vars.URL_TS_FIELD
        if self.check_is_massival_inner_user():
            ret_dict['get_source_url'] = global_vars.URL_ADMIN_TS_FIELD
        uri = '/%s/%s'%(self.my_uid, view_util.gen_uuid())
        ret_dict['uri'] = uri
        return ret_dict

    def domain_handler(self, domains):
        return [i.split(";")[0] for i in domains.split(",")]

    def output_list(self):
        # select all by sorting
        lander_domain = self.args.get('lander_domain')
        track_domain = self.args.get("track_domain")
        offer_id = self.args.get("offer")

        d = {
            'cur_url' : request.path,
            'create_url' : make_url(global_vars.URL_CAMP_CREATE, {'url' : request.path}),
            'set_hidden_url' : global_vars.URL_CAMP_SET_HIDDEN,
            'get_source_url' : global_vars.URL_TS_FIELD,
        }

        if self.check_is_massival_inner_user():
            d['get_source_url'] = global_vars.URL_ADMIN_TS_FIELD

        if lander_domain or track_domain:
            if lander_domain:
                main_domain = lander_domain
            else:
                main_domain = track_domain

            tmp_rows = self.db_client.iter_all(self.table_class, uid=self.my_uid)
            rows = []
            for row in tmp_rows:
                if lander_domain:
                    domains_list = row.lander_domains_dist
                else:
                    domains_list = row.track_domain
                domains = [s.split(";")[0].strip() for s in domains_list.split(',') if s.strip()]
                found = False
                for _domain in domains:
                    found = is_subdomain(_domain, [main_domain])
                    if found:
                        break
                if found:
                    rows.append(row)
        elif offer_id:
            paths = self.db_client.iter_all(Path, uid=self.my_uid)
            swaps = self.db_client.iter_all(SwapRotation, uid=self.my_uid)
            flows = self.db_client.iter_all(Flow, uid=self.my_uid)
            camps = self.db_client.iter_all(Campaign, uid=self.my_uid)

            d['showAll'] = True
            rows = OfferView.get_camp_by_oid(int(offer_id), camps, flows, swaps, paths)
        else:
            rows = self.db_client.iter_all(self.table_class, uid=self.my_uid)

        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        filter_cols = ['uid', 'ck_cloak', 'ck_cloak_html', 'ck_cloak_ts', 'ck_cloak_ts_html', 'ck_android', 'ck_android_html', 'ck_websiteid_digit', 'ck_websiteid_typo', 'ck_websiteid_html', 'ck_meta_refresh', 'ck_cloak_ts2', 'ck_cloak_ts_html2']
        name_filter = ['id', 'uid', 'hidden', 'ck_cloak', 'ck_cloak_html', 'ck_cloak_ts', 'ck_cloak_ts_html', 'ck_android', 'ck_android_html', 'ck_websiteid_digit', 'ck_websiteid_typo', 'ck_websiteid_html', 'ck_meta_refresh', 'ck_cookie', 'ck_cookie_time', 'ck_cookie_html', 'ck_touch', 'ck_touch_html', 'ck_cloak_ts2', 'ck_cloak_ts_html2']
        name2title = {}
        domain_fields = ['lander_domains_dist', 'track_domains']

        flows = self.db_client.select_all(Flow, uid=self.my_uid)

        flow_cache = {}
        source_cache = {}
        admin_source_cache = {}

        for f in flows:
            flow_cache[f.id] = f.name

        foreignkey2name = {
            'flow_id':{'name':'flow', 'cache':flow_cache},
        }

        if self.is_inner_user:
            name_filter.append("source_id")
            filter_cols.append("source_id")
            admin_sources = self.get_admin_config(AdminTrafficSource)
            for f in admin_sources:
                admin_source_cache[f.id] = f.name
            foreignkey2name['admin_source_id'] = {'name':'admin_source', 'cache':admin_source_cache}
        else:
            name_filter.append("admin_source_id")
            filter_cols.append("admin_source_id")
            sources = self.db_client.select_all(TrafficSource, uid=self.my_uid)
            for f in sources:
                source_cache[f.id] = f.name
            foreignkey2name['source_id'] = {'name':'source', 'cache':source_cache}

        field_names = []
        extra_name_cols = ["admin_source_id", "source_id"]
        for col in columns:
            if col.name in name_filter:
                continue
            t = "string" if col.is_foreign or isinstance(col.real_column.type, String) or col.name in extra_name_cols  else "number"
            col_ret = { 'name' :col.name, 'type': t}
            title = name2title.get(col.name, None)
            if title is not None:
                col_ret['title'] = title

            parse = foreignkey2name.get(col.name, None)
            if parse is not None:
                col_ret['name'] = parse['name']
            field_names.append(col_ret)

        d['field_names'] = field_names
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
                        #ids = [_id for _id in vs.split(',')]
                        options = self.get_multi_options(column.multi_table, column.multi_id, 'name')
                        ret_names = []
                        for _id in ids:
                            ret_names.append(options.get(_id, 'unknown'))
                        tmp_records[column.name] = ','.join(ret_names)
                    else:
                        if column.is_textarea:
                            tmp_records[column.name] = ('[CONTENT CANNOT READ]')
                        else:
                            val = getattr(row, column.name)
                            if column.name in ["admin_source_id", "source_id"]:
                                _fid = getattr(row, column.name)
                                tmp_records[column.name] = _fid
                                i = foreignkey2name[column.name]
                                cache = i['cache']
                                v = cache[val]
                                tmp_records[i['name']] = (v)
                            else:
                                if column.name in domain_fields:
                                    val = self.domain_handler(val)
                                tmp_records[column.name] = val

                elif column.is_foreign and column.name not in ['uid']:
                    _fid = getattr(row, column.name)
                    tmp_records[column.name] = _fid
                    if column.name in foreignkey2name:
                        i = foreignkey2name[column.name]
                        cache = i['cache']
                        source_col = column.foreign_source_key
                        v = cache[_fid]

                        tmp_records[i['name']] = (v)

            obj_info = {}
            obj_info['values'] = tmp_records
            obj_info['edit_url'] = make_url(global_vars.URL_CAMP_EDIT, {'url' : request.path, 'id' : pk_id})
            obj_info['id'] = pk_id
            records.append(obj_info)

        def _cmp(a, b):
            return int(b["id"]) - int(a["id"]) 
        records = sorted(records, _cmp)

        d['records'] = records
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
            camp = self.db_client.select_one(Campaign, id=i)
            if camp:
                camp.hidden = t
                self.db_client.do_save(camp)

        return redirect(back)

    def output_create(self, is_create, custom_tips=None, custom_op_tips=None):
        is_clone = True if self.args.get('clone') else False
        (new_args, error_args) = self.check_create_args() if is_create else (self.args, {})

        has_errors = len(error_args) > 0
        err_msg = ''

        if not has_errors and is_create and not is_clone:
            cpid = self.add_one(**new_args)
            assert type(cpid) == int
            self.args['id'] = cpid
            return redirect("%s?id=%d&create=1"%(global_vars.URL_CAMP_EDIT, cpid))

        if custom_op_tips is not None:
            op_tips = custom_op_tips
        elif is_clone:
            op_tips = ""
            pop_fields = ["id", "uri"]
            new_args['name'] += "-copy"
            [new_args.pop(f) for f in pop_fields if new_args.get(f) is not None]
        else:
            if has_errors:
                op_tips = gen_op_tips('Create Failed! %s'%err_msg)
            else:
                op_tips = gen_op_tips('Create Success!', True)

        ret_dict = self.init_static_data(op_tips)
        ret_dict['tips'] = {}

        if has_errors or is_clone:
            ret_dict.update(new_args)
        filter_cols = ['uid', 'swap_id']

        for col in self.table_class.__table__.columns:
            if col.name in error_args:
                ret_dict['tips'][col.name] = gen_tips()
            for k in self.table_class.__table__.foreign_keys:
                if k.parent == col and col.name not in filter_cols:
                    func = self.get_options.get(col.name, self.get_default_options)
                    ret_dict['options'].update(func(k, 'name', col.name))
                    break
        ret_dict['options'].update(self.get_lander_offer_options())
        ret_dict['options'].update(self.get_track_domains_options())
        ret_dict['options'].update(self.get_source_options())
        ret_dict['country_config'] = country_config.COUNTRY_NAME_LIST
        ret_dict['check_offer_url'] = global_vars.URL_CAMP_CHECK_OFFER
        #ret_dict["campaign_update_cost"] = self.render_campaign_update_cost()
        ret_dict["campaign_update_cost"] = ""
        ret_dict["get_switch_path_url"] = global_vars.URL_SWITCH_PATH_GET
        ret_dict["save_switch_path_url"] = global_vars.URL_SWITCH_PATH_SAVE
        ret_dict["is_inner_user"] = self.is_inner_user
        return self.load_tmp(ret_dict, CREATE_TMPL_PATH)

    def load_rule_tmp(self, tmp_path="rule_modal.tmpl", rules={}):
        ret_dict = {}
        ret_dict['rules'] = ujson.dumps(rules)
        ret_dict['rule_config'] = rule_config
        ret_dict['sec_cate_url'] = global_vars.URL_CAMP_RULE_SEC_CATE
        ret_dict['get_rule_url'] = global_vars.URL_CAMP_GET_RULE
        rule_tmp = self.tmpl_reader.read_file(tmp_path)
        return Template(rule_tmp).render(**ret_dict)

    def load_tmp(self, ret_dict, tmp_path):
        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def get_lander_offer_options(self):
        lander_records = self.db_client.select_all(LandingPage, uid=self.my_uid)
        offer_records = self.db_client.select_all(Offer, uid=self.my_uid)
        return {'lander': lander_records, 'offer': offer_records}

    def get_track_domains_options(self):
        user = self.db_client.select_one(User, id=self.my_uid)
        return {'track_domains':self.domain_handler(user.track_domains)}
    
    def get_source_options(self):
        ret_dict = {}
        if self.check_is_massival_inner_user():
            ret_dict["source_id"] = self.get_admin_config(AdminTrafficSource)
        else:
            objs = self.db_client.iter_all(TrafficSource, uid=self.my_uid)
            ret_dict["source_id"] = objs
        return ret_dict

    def get_default_options(self, foreign_source_key, tag_name, key_name):
        table_name = foreign_source_key.target_fullname.split('.')[0]
        pk_name = foreign_source_key.target_fullname.split('.')[1]
        tb_class = self.name2table.get(table_name)
        records = self.db_client.select_all(tb_class, uid=self.my_uid)
        return {key_name: records}

    def get_foreign_key_field_data(self, foreign_source_key, tag_name, key_name, fid):
        table_name = foreign_source_key.target_fullname.split('.')[0]
        pk_name = foreign_source_key.target_fullname.split('.')[1]
        tb_class = self.name2table.get(table_name)
        rec = self.db_client.select_one(tb_class, id=fid, uid=self.my_uid)
        return getattr(rec, tag_name)

    def do_update(self, **kargs):
        new_kargs = view_util.filter_model_key(self.table_class, kargs)
        model = self.table_class(**new_kargs)
        try:
            assert self.db_client.do_save(model)
        except Exception, ex:
            return str(ex)
        return ""


    def output_edit1(self):
        new_args, error_args = view_util.check_primary_args(self.args, self.table_class, self.name2table, self.db_client, True)

        has_errors = len(error_args) > 0

        filter_dict = {'id': new_args['id'], 'uid': self.my_uid}

        reload_record = self.db_client.select_one(self.table_class, **filter_dict)
        if self.args.get('create'):
            op_tips = gen_op_tips('Create Success!', True)
        else:
            op_tips = ""
        return self.output_edit(reload_record, new_args, error_args, op_tips=op_tips)

    def output_edit2(self):
        new_args, error_args = self.check_create_args(True)
        has_errors = len(error_args) > 0


        error_msg = ''
        if not has_errors:
            assert self.do_update(**new_args) == ""

        reload_record = self.table_class(**new_args)
        if has_errors:
            op_tips = gen_op_tips('Edit Failed! %s'%error_msg)
        else:
            op_tips = gen_op_tips('Edit Success!', True)
        return self.output_edit(reload_record, new_args, error_args, op_tips=op_tips)

    def __match_campaign_cost(self, cpid, cost, ts):
        self.init_campaign_cost(cpid)
        last_cost= None
        cost_list = self._campaign_cost_list
        for i in xrange(len(cost_list)):
            start_ts, timezone, cost = cost_list[i]
            diff_ts = (_TIMEZONE - timezone) * 3600
            if ts >= start_ts + diff_ts:
                last_cost = cost
        return last_cost

    def output_edit(self, reload_record, new_args, error_args, custom_tips=None, op_tips=None):
        has_errors = len(error_args) > 0
        err_msg = ''

        if custom_tips is not None:
            op_tips = custom_tips

        ret_dict = self.init_static_data(op_tips, create=False)

        filter_cols = ['uid', 'swap_id']

        for col in self.table_class.__table__.columns:
            if col.name in error_args:
                msg = error_args[col.name]
                if msg == "miss" or msg == "select":
                    ret_dict['tips'][col.name] = gen_tips()
                else:
                    ret_dict['tips'][col.name] = gen_tips(msg)
            for k in self.table_class.__table__.foreign_keys:
                if k.parent == col and col.name not in filter_cols:
                    func = self.get_options.get(col.name, self.get_default_options)
                    ret_dict['options'].update(func(k, 'name', col.name))
                    break
            ret_dict[col.name] = getattr(reload_record, col.name)
        cost = ret_dict["cost"]
        new_cost = self.__match_campaign_cost(ret_dict["id"], cost, int(time.time())) or cost
        ret_dict["update_campaign_cost_tips"] = "" if cost == new_cost else gen_update_campaign_cost_tips(new_cost)
        ret_dict['country_config'] = country_config.COUNTRY_NAME_LIST
        ret_dict['options'].update(self.get_lander_offer_options())
        ret_dict['options'].update(self.get_track_domains_options())
        ret_dict['options'].update(self.get_source_options())
        ret_dict['duplicate_url'] = global_vars.URL_CAMP_CREATE
        ret_dict['check_offer_url'] = global_vars.URL_CAMP_CHECK_OFFER
        ret_dict['check_camp_url'] = global_vars.URL_CHECK_CAMPAIGN
        ret_dict["campaign_update_cost"] = self.render_campaign_update_cost(ret_dict)
        ret_dict["get_switch_path_url"] = global_vars.URL_SWITCH_PATH_GET
        ret_dict["save_switch_path_url"] = global_vars.URL_SWITCH_PATH_SAVE
        ret_dict["allow_switch_path"] = self.check_permission(PERMISSION_CONFIGURE, PERMISSION_CONFIGURE_SWITCH_PATH)
        ret_dict["is_inner_user"] = self.is_inner_user
        return self.load_tmp(ret_dict, EDIT_TMPL_PATH)

    @staticmethod
    def get_sec_cate_json():
        args = view_util.get_request_args()
        cate_id = int(args['id'])
        ret = rule_config.rule_second_category[cate_id]
        return ujson.dumps(ret)

    @staticmethod
    def check_offer_country(cookies):
        args = view_util.get_request_args()
        fid = args['flow_id']
        country = args['country']
        db_client = DBSet.get_db_client()

        uid = view_util.username2uid(cookies['username'], db_client)
        flow = db_client.select_one(Flow, id=int(fid))

        swaps = model_to_dict(db_client.iter_all(SwapRotation, uid=uid))
        paths = model_to_dict(db_client.iter_all(Path, uid=uid))
        offers = model_to_dict(db_client.iter_all(Offer, uid=uid))

        ret = {}

        for sid in flow.swaps.split(","):
            sid = int(sid)
            swap = swaps[int(sid)]
            for path_str in swap.paths.split(","):
                pid, weight = path_str.split(";")
                if not int(weight): continue
                path = paths[int(pid)]
                for oid in path.offers.split(","):
                    offer = offers[int(oid)]
                    country_list = offer.country.split(",")
                    if country not in country and "GLOBAL" not in offer.country:
                        if swap.name not in ret:
                            ret[swap.name] = {}
                        if path.name not in ret[swap.name]:
                            ret[swap.name][path.name] = []
                        ret[swap.name][path.name].append(offer.name)
        return ret


    @staticmethod
    def get_rule(session_info):
        args = view_util.get_request_args()
        index = int(args['index'])
        campaign_id = int(args['id'])

        campaign_model = DBSet.get_db_client().select_one(Campaign, id=int(args['id']))


        rules = ujson.loads(campaign_model.rules)
        ret_rule = []
        if len(rules) > index:
            rule = rules[index]
            for condition in rule['condition']:
                ret_rule.append([rule_config.rule[i] for i in condition['rules']])
        return ujson.dumps(ret_rule)

    @staticmethod
    def update_campaign_cost(session_info, cpid, start_time, timezone, cost):
        #check campaign update cost args
        uid = view_util.username2uid(session_info['username'], DBSet.get_db_client())
        args = dict(
            uid = uid, cpid = cpid,
            cost = cost, start_time = start_time,
            timezone = timezone
        )
        try:
            model = CampaignCost(**args)
            DBSet.get_db_client().do_save(model)
        except Exception, ex:
            print ex
            return False
        return True

    @staticmethod
    def get_campaign_update_list(session_info, cpid):
        uid = view_util.username2uid(session_info['username'], DBSet.get_db_client())
        campaings = DBSet.get_db_client().iter_all(CampaignCost, uid=uid,cpid=cpid)
        data= []
        for obj in campaings:
            data.append([obj.start_time, obj.timezone, obj.cost])
        data.sort(lambda x,y:cmp(x[0],y[0]), reverse=True)
        cnt = 0
        result = []
        for info in data:
            dt = datetime.datetime.fromtimestamp(info[0])
            datetime_str = dt.strftime('%Y-%m-%d %H:00')
            info[0] = datetime_str
            result.append(info)
            cnt += 1
            if cnt >= 5:
                break
        return result

    def render_campaign_update_cost(self, args):
        uid = self.my_uid
        cpid = self.args["id"]
        campObj = self.db_client.select_one(Campaign, uid=uid, id=cpid)
        cpname = campObj.name if campObj else cpid
        ret_dict = {
            "cpid" : cpid,
            "name" : cpname,
            "cost" : args["cost"]
        }
        render = Render('Mobitx Update Cost %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file("campaign_update_cost.tmpl")
        body_str = Template(body_tmpl).render(**ret_dict)
        return body_str

    def __obj2list(self, objs):
        res = {}
        for o in objs:
            res[o.id] = o
        return res

    def get_switch_path(self):
        flow_id = int(self.args['flow_id'])
        flow = self.db_client.select_one(Flow, id=flow_id)
        swap_ids = flow.swaps.split(",")

        result = {}
        swap_result = {}
        swaps = self.__obj2list(self.db_client.iter_all(SwapRotation, uid=self.my_uid))
        paths = self.__obj2list(self.db_client.iter_all(Path, uid=self.my_uid))
        for swap_id in swap_ids:
            swap_id = int(swap_id)
            if swap_id not in swaps:
                continue
            result.setdefault(swap_id, {})
            swap_result[swap_id] = swaps[swap_id].name
            path_ids = swaps[swap_id].paths.split(",")
            for path_info in path_ids:
                tmp = path_info.split(";")
                path_id = int(tmp[0])
                w = int(tmp[1])
                if path_id not in paths:
                    continue
                result[swap_id][path_id] = "%s(%s)" % (paths[path_id].name, w)
        rules = {}
        rulesObj = self.db_client.select_one(SwitchPath, uid=self.my_uid, flow_id=flow_id)
        data = {
            "swaps" : swap_result,
            "paths" : result,
            "rules" : rulesObj.rules if rulesObj else "",
            "sp_id" : rulesObj.id if rulesObj else None,
        }
        return ujson.dumps(data)

    def save_switch_path(self):
        cpid = int(self.args['cpid'])
        flow_id = int(self.args['flow_id'])
        sp_id = int(self.args['sp_id'])

        swap_ids = self.args["swap_ids"].split(",")
        master_ids = self.args['master_ids'].split(",")
        slave_ids = self.args['slave_ids'].split(",")
        rule_list = []
        for idx in xrange(len(swap_ids)):
            swap = swap_ids[idx]
            master = master_ids[idx]
            slave = slave_ids[idx]
            if swap == "" or master == "" or slave == "":
                continue
            r = "%s|%s|%s" % (swap, master, slave)
            rule_list.append(r)

        rules = ";".join(rule_list)
        res = {
            "tips" : "",
            "ok" : True
        }
        try:
            args = {
                "uid" : self.my_uid,
                "cpid" : cpid,
                "flow_id" : flow_id,
                "rules" : rules,
            }
            if sp_id > 0:
                args["id"] = sp_id
            model = SwitchPath(**args)
            ok = self.db_client.do_save(model)
            res["tips"] = "save successed." if ok else "save failed."

        except Exception, ex:
            print ex
            res["ok"] = False
            res["tips"] = "except save failed."
        return ujson.dumps(res)


