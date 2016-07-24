#!/usr/bin/env python

# -*- coding:utf-8 -*-

import ujson
import uuid
import settings
import global_vars
from sqlalchemy import Integer, String, Float
from mako.template import Template
from flask import request
from sqlalchemy.exc import IntegrityError
from config import country_config
from db_client import get_normal_columns, get_primary_keys, \
        get_foreign_source_keys, get_foreign_keys, \
        get_nonprimary_columns, get_columns, User
from utils import get_model_uri, make_url, to_links, to_links_custom, check_is_massival_inner_user, check_permission, decode_from_utf8
from views import view_util
from global_vars import global_db_set as DBSet
from commlib.db.db_tabledef import virus_domains_key, virusdomains_admin_table, verify_domains_key
from config.auth_config import SUPER_ADMIN_UID

def get_request_args():
    d1 = request.args.to_dict()
    d2 = request.form.to_dict()
    d1.update(d2)
    return d1

def gen_op_tips(tips, success=False):
    if not success:
        return '''<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></div>'''%tips
    else:
        return '''<div class="alert alert-success"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></div>'''%tips


def gen_tips():
    return '''<div><span class="label label-important">Field Is Required</span></div>'''


def gen_uuid():
    return str(uuid.uuid4()).replace('-', '')

class Render(object):
    def __init__(self, title, tmpl_reader, session_info, **custom_tmpl):
        self.title = title
        self.tmpl_reader = tmpl_reader
        self.session_info = session_info

        self.tmpls = {
            'index' : 'index.tmpl',
            'header' : 'header.tmpl',
            'footer' : 'footer.tmpl',
            'nav_top' : 'nav_top.tmpl',
            'nav_left' : 'nav_left.tmpl',
        }

        self.tmpls.update(custom_tmpl)

    def init_domains_tips(self, user):
        domains = [i.split(";")[0] for i in user.lander_domains.split(",")] if user.lander_domains else []
        domains.extend([i.split(";")[0] for i in user.track_domains.split(",")] if user.track_domains else [])
        virus_num = 0
        verify_num = 0
        virus_data = DBSet.get_redis_db().get_all(virusdomains_admin_table)
        verify_data = DBSet.get_redis_db().get_all(verify_domains_key)

        for url in domains:
            virus_ret = virus_data.get(url)
            verify_ret = verify_data.get(url)
            if virus_ret:
                url_ret = ujson.loads(virus_ret)
                virus_num += 1 if url_ret['positives'] > 0 else 0
            if verify_ret:
                url_ret = ujson.loads(verify_ret)
                verify_num += 0 if url_ret['ret'] >= 0 else 1

        return (verify_num, virus_num) if verify_num != 0 or virus_num != 0 else False

    def gen_output(self, body_str, tmpl_dict=None):
        index_tmpl = self.tmpl_reader.read_file(self.tmpls['index'])
        header_tmpl = self.tmpl_reader.read_file(self.tmpls['header'])
        footer_tmpl = self.tmpl_reader.read_file(self.tmpls['footer'])
        navtop_tmpl = self.tmpl_reader.read_file(self.tmpls['nav_top'])
        navleft_tmpl = self.tmpl_reader.read_file(self.tmpls['nav_left'])

        from db_client import User
        username = self.session_info["username"]
        user = DBSet.get_db_client().select_one(User, name=username)

        domain_info = self.init_domains_tips(user)

        d = {
            'title' : self.title,
        }
        header_str = Template(header_tmpl).render(**d)

        if tmpl_dict is None:
            tmpl_dict = {}
        tmpl_dict['info'] = {}
        tmpl_dict['info'][global_vars.DOMAIN_INFO] = "%s+%s"%domain_info if domain_info else ""

        nav_top_tmpl_dict = {}
        nav_top_tmpl_dict.update(self.session_info)

        d = {
            'header' : header_str,
            'footer' : footer_tmpl,
            'nav_top' : Template(navtop_tmpl).render(**nav_top_tmpl_dict),
            'nav_left' : Template(navleft_tmpl).render(**tmpl_dict),
            'body' : body_str,
        }
        index_str = Template(index_tmpl).render(**d)
        return index_str


class LoginRender(object):
    def __init__(self, title, tmpl_reader):
        self.title = title
        self.tmpl_reader = tmpl_reader

    def gen_output(self, body_str):
        index_tmpl = self.tmpl_reader.read_file('index2.tmpl')

        d = {
            'body' : body_str,
            'title' : self.title,
        }
        index_str = Template(index_tmpl).render(**d)
        return index_str


def get_multi_table(table_class, col_name):
    from db_client import SwapRotation
    from db_client import Path
    from db_client import Offer
    from db_client import LandingPage

    if table_class == Path and col_name == 'offers':
        return Offer
    if table_class == Path and col_name == 'landing_pages':
        return LandingPage
    if table_class == SwapRotation and col_name == 'paths':
        return Path
    return None


def is_disable(table_class, col_name):
    from db_client import Campaign
    if table_class == Campaign and col_name == 'uri':
        return True
    else:
        return False


class BaseColumn(object):
    def __init__(self, real_column, table_class):
        self.real_column = real_column
        self.name = self.real_column.name
        self.table_class = table_class
        self.is_primary = real_column.name in set([i.name for i in get_primary_keys(self.table_class)])
        self.is_foreign = real_column.name in set([i.name for i in get_foreign_keys(self.table_class)])
        self.is_normal = not self.is_primary and not self.is_foreign
        self.is_disable = is_disable(self.table_class, self.name)

        self.multi_table = get_multi_table(self.table_class, self.name)
        self.is_multi = self.multi_table is not None
        self.multi_id = 'id'

        #self.is_textarea = self.name == 'page_source'
        self.is_textarea = False


        self.foreign_key = None
        self.foreign_source_key = None
        for i in table_class.__table__.foreign_keys:
            if self.real_column == i.parent:
                self.foreign_key = self.real_column
                self.foreign_source_key = i
                break



class ReportView(object):
    def __init__(self, title, tmpl_reader, session_info, url, uid, **custom_tmpl):
        self.title = title
        self.tmpl_reader = tmpl_reader
        self.session_info = session_info
        self.url = url
        self.uid = uid

    def gen_output(self, body_str):
        render = Render(self.title, self.tmpl_reader, self.session_info)
        #return render.gen_output(body_str, {'nav_left' : to_report_links(self.url, self.uid)})
        return render.gen_output(body_str, {'nav_left' : to_links_custom(self.url)})


__ALLOW_FILES = ['html']
def allow_file(filename):
    return '.' in filename and \
               filename.rsplit('.', 1)[1] in __ALLOW_FILES

LANDPAGE_OP_CREATE_SHOW = 0
LANDPAGE_OP_CREATE = 1
LANDPAGE_OP_EDIT_SHOW = 2
LANDPAGE_OP_EDIT = 3

class LandpageView(object):
    def __init__(self, table_class, session_info):
        self.args = get_request_args()
        self.table_class =  table_class
        self.tmpl_reader = global_vars.tmpl_reader
        self.db_client = DBSet.get_db_client()
        self.session_info = session_info
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table

        url_name = self.table_class.__tablename__.replace('_', '').lower()
        self.list_url = get_model_uri(self.table_class, 'list')
        self.edit_url = get_model_uri(self.table_class, 'edit')
        self.create_url = get_model_uri(self.table_class, 'create')
        self.del_url = get_model_uri(self.table_class, 'del')
        self.campaign_check_url = global_vars.URL_CHECK_CAMPAIGN
        self.batch_upload_url = global_vars.URL_LP_BATCH_UPLOAD

        self.list_tmpl = 'landingpage_list.tmpl'
        self.create_tmpl = 'landingpage_create.tmpl'
        self.edit_tmpl = 'landingpage_edit.tmpl'

        self.lp_tmpl = 'landingpage_show.tmpl'
        self.campaign_check_tmpl = 'campaign_check.tmpl'

        self.username = session_info['username']
        self.my_uid = self.username2uid(self.username)
        self.args['uid'] = self.my_uid

        self._op_func = {
            LANDPAGE_OP_CREATE : ("create", self._output_lp_create),
            LANDPAGE_OP_CREATE_SHOW : ("create", None),
            LANDPAGE_OP_EDIT_SHOW : ("edit", self._output_lp_edit_show),
            LANDPAGE_OP_EDIT : ("edit", self._output_lp_edit),
        }

        self._filter_col = ['uid', 'hidden', 'page_source']

    def username2uid(self, username):
        from db_client import User
        user = self.db_client.select_one(User, name=username)
        return user.id

    def output_list(self):
        # select all by sorting
        sort_arg = self.args.get('sort')
        if sort_arg is None:
            rows = self.db_client.select_all(self.table_class, uid=self.my_uid)
        else:
            idx = int(sort_arg)
            sort_arg = get_columns(self.table_class)[idx].asc()
            rows = self.db_client.select_all_sort(self.table_class, sort_arg, uid=self.my_uid)

        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        filter_cols = ['uid']

        filter_name= ['source']
        field_names = []
        for col in columns:
            t = "string" if isinstance(col.real_column.type, String) else "number"
            if col.name in filter_name:
                continue
            if col.is_normal:
                field_names.append({
                    'name' :col.name,
                    'is_normal' : True,
                    'type' : t,
                })

            if col.is_foreign and col.name not in filter_cols:
                field_names.append({
                    'name' : col.name,
                    'is_normal' : False,
                    'type' : "string",
                })

        records = []
        for row in rows:
            tmp_records = {}
            pk_id = None
            for column in columns:
                if column.name in filter_name:
                    continue
                if column.is_primary:
                    pk_id = getattr(row, column.name)

                if column.is_normal:
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
                            tmp_records[column.name] = '[CONTENT CANNOT READ]'
                        else:
                            tmp_records[column.name] = getattr(row, column.name)

                if column.is_foreign and column.name not in filter_cols:
                    source_col = column.foreign_source_key
                    options = self.get_options(source_col, 'name')
                    _fid = getattr(row, column.name)
                    v = options.get(_fid, 'UNKNOWN')
                    tmp_records[column.name] = v

            obj_info = {}
            obj_info['values'] = tmp_records
            obj_info['edit_url'] = make_url(self.edit_url, {'url' : request.path, 'id' : pk_id})
            obj_info['id'] = pk_id
            records.append(obj_info)

        d = {
            'cur_url' : request.path,
            'create_url' : make_url(self.create_url, {'url' : request.path}),
            'del_url' : self.del_url,
            'campaign_check_url' : self.campaign_check_url,
            'batch_upload_url' : self.batch_upload_url,
            'field_names' : field_names,
            'records' : records,
        }

        title = '2Fly %s List'%self.table_class.__name__
        render = Render(title, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.list_tmpl)
        body_str = Template(body_tmpl).render(**d)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def output_create1(self):
        return self.output_create(False, '', '')

    def output_create2(self):
        return self.output_create(True)

    def output_campaign_check(self, args):
        url = {
            'list_url' : make_url(self.list_url, {'url' : request.path}),
            'create_url' : make_url(self.create_url, {'url' : request.path}),
        }
        args.update(url)
        title = '2Fly %s List'%self.table_class.__name__
        render = Render(title, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.campaign_check_tmpl)
        body_str = Template(body_tmpl).render(**args)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def _read_upload_files(self, is_single=True):
        upload_files = request.files.getlist("upload_files")
        if len(upload_files) == 0:
            return dict(ok=False, err="please choose file.")

        if is_single and len(upload_files) > 1:
            return dict(ok=False, err="only allow upload one file.")
        source = ""
        for file in upload_files:
            if not allow_file(file.filename):
                return dict(ok=False, err="only allow upload html file")
            for line in file.stream:
                source = "%s%s" % (source, line)
        return dict(ok=True, err="", source=source)

    def _render_lp_html(self, args, tag):
        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)

        body_tmpl = self.tmpl_reader.read_file(self.lp_tmpl)
        body_str = Template(body_tmpl).render(**args)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def _init_render_args(self):
        rect = {}
        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]
        for col in columns:
            if col.name in self._filter_col:
                continue
            t = "string" if isinstance(col.real_column.type, String) else "number"
            if t == "string":
                rect[col.name] = ""
            elif t == "number":
                rect[col.name] = 0
        return rect

    def _gen_render_args(self, record):
        rect = {}
        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]
        for col in columns:
            if col.name in self._filter_col:
                continue
            t = "string" if isinstance(col.real_column.type, String) else "number"
            rect[col.name] = getattr(record, col.name)
            if t == "string" and rect[col.name] is None:
                rect[col.name] = ""
        return rect

    def _output_lp_create(self, ret_dict):
        if self.args.has_key("name") and self.args["name"] == "":
            ret_dict["op_tips"] = gen_op_tips('Create Failed! %s'%"name is not allow empty.")
            return ret_dict

        if self.args.has_key("upload"):
            ret = self._read_upload_files()
            if not ret["ok"]:
                ret_dict["op_tips"] = gen_op_tips('Create Failed! %s'%ret["err"])
                return ret_dict
            self.args["source"] = ret["source"]

        self.args["source"] = self.args["source"].encode("utf-8")
        new_args, error_args = check_create_args(self.args, self.table_class, self.name2table, self.db_client)
        has_errors = len(error_args) > 0
        err_msg = ''

        if not has_errors:
            model = self.table_class(**new_args)
            try:
                self.db_client.do_save(model)
            except Exception, ex:
                has_errors = True
                err_msg += str(ex)

        if has_errors:
            op_tips = gen_op_tips('Create Failed! %s'%err_msg)
        else:
            op_tips = gen_op_tips('Create Success!', True)

        ret_dict['op_tips'] = op_tips
        ret_dict['name'] = ''
        ret_dict['source'] = ''
        return ret_dict

    def _output_lp_edit_show(self, ret_dict):
        # show only
        new_args, error_args = check_primary_args(self.args, self.table_class, self.name2table, self.db_client, True)

        has_errors = len(error_args) > 0
        assert not has_errors

        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]
        filter_dict = {}
        for col in columns:
            if col.is_primary:
                filter_dict[col.name] = new_args[col.name]

        reload_record = self.db_client.select_one(self.table_class, **filter_dict)
        rect = self._init_render_args()
        if reload_record:
            rect = self._gen_render_args(reload_record)
            rect['source'] = decode_from_utf8(rect['source'])

        ret_dict.update(rect)
        ret_dict["link"] = make_url(ret_dict['tag'], {'url' : request.path, 'id' : ret_dict["id"]})
        return ret_dict

    def _output_lp_edit(self, ret_dict):
        # edit only
        new_args, error_args = check_create_args(self.args, self.table_class, self.name2table, self.db_client, True)
        has_errors = len(error_args) > 0

        if not has_errors and self.args.has_key("upload"):
            ret = self._read_upload_files()
            if not ret["ok"]:
                ret_dict["op_tips"] = gen_op_tips('Edit Failed! %s'%ret["err"])
                ret_dict.update(self._gen_render_args(self.args))
                return ret_dict
            self.args["source"] = ret["source"]
            new_args["source"] = ret["source"]

        s = new_args["source"].encode("utf-8")
        new_args["source"] = s
        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]
        error_msg = ''
        filter_dict = {}
        update_dict = {}
        if not has_errors:
            for col in columns:
                if col.is_primary:
                    filter_dict[col.name] = new_args[col.name]
                elif new_args.get(col.name) is not None:
                    update_dict[col.name] = new_args[col.name]

            filter_dict['uid'] = self.my_uid
            try:
                self.db_client.do_update(self.table_class, filter_dict, update_dict)
            except Exception, ex:
                print Exception, ex
                error_msg = str('update failed')
                has_errors = True
        else:
            filter_dict['uid'] = self.my_uid

        reload_record = None
        #if not is_edit and not has_errors:
        reload_record = self.db_client.select_one(self.table_class, **filter_dict)

        _id = self.args.get("id", 0)
        rect = self._init_render_args()
        rect["id"] = _id
        if has_errors:
            op_tips = gen_op_tips('Edit Failed! %s'%error_msg)
        else:
            op_tips = gen_op_tips('Edit Success!', True)

        if reload_record:
            rect = self._gen_render_args(reload_record)

        ret_dict.update(rect)
        ret_dict["op_tips"] = op_tips
        ret_dict['link'] = make_url(ret_dict['tag'], {'url' : request.path, 'id' : _id})
        return ret_dict

    def output_lp_html(self, op):
        ret_dict = {}
        ret_dict.update(self._init_render_args())
        ret_dict['list_url'] = self.list_url
        ret_dict['batch_upload_url'] = self.batch_upload_url
        ret_dict['op_tips'] = ''
        ret_dict['tag'] = 'normal'
        ret_dict["link"] = ""

        self.args["page_source"] = ""
        func = self._op_func.get(op, None)
        if func:
            ret_dict['tag'] = func[0]
            ret_dict['link'] = func[0]
            if func[1]:
                ret_dict = func[1](ret_dict)
                ret_dict["source"] = ret_dict["source"].replace('"', "&quot;")
                ret_dict["source"] = ret_dict["source"].replace('<', "&lt;")
                ret_dict["source"] = ret_dict["source"].replace('>', "&gt;")

        return self._render_lp_html(ret_dict, func[0])

    def output_create(self, is_create, custom_tips=None, custom_op_tips=None):
        new_args, error_args = check_create_args(self.args, self.table_class, self.name2table, self.db_client)
        has_errors = len(error_args) > 0
        err_msg = ''

        if not has_errors and is_create:
            model = self.table_class(**new_args)
            try:
                self.db_client.do_save(model)
            except Exception, ex:
                has_errors = True
                err_msg += str(ex)

        if has_errors:
            op_tips = gen_op_tips('Create Failed! %s'%err_msg)
        else:
            op_tips = gen_op_tips('Create Success!', True)
        #op_tips = '''<div class="alert alert-success"><strong>Create Success!</strong></div>'''

        if custom_op_tips is not None:
            op_tips = custom_op_tips

        ret_dict = {}
        ret_dict['list_url'] = self.list_url
        ret_dict['op_tips'] = op_tips
        ret_dict['fields'] = []
        ret_dict['country_config'] = country_config.COUNTRY_NAME_LIST

        filter_cols = ['uid']
        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]
        for col in columns:
            if col.is_primary:
                continue
            if col.is_foreign and col.name in filter_cols:
                continue

            d = {}
            d['name'] = col.name
            if custom_tips is None:
                d['tips'] = gen_tips() if col.name in error_args else ''
            else:
                d['tips'] = custom_tips
            d['is_normal'] = col.is_normal
            d['is_multi'] = col.is_multi
            d['is_textarea'] = col.is_textarea
            d['is_disable'] = col.is_disable
            if col.is_foreign and col.name not in filter_cols:
                source_col = col.foreign_source_key
                options = self.get_options(source_col, 'name')
                d['items'] = options.items()
            if col.is_multi:
                options = self.get_multi_options(col.multi_table, col.multi_id, 'name')
                d['items'] = options.items()
            if col.is_disable:
                uri = '/%s/%s'%(self.my_uid, gen_uuid())
                d['disable_value'] = uri
            ret_dict['fields'].append(d)

        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)

        body_tmpl = self.tmpl_reader.read_file(self.create_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def output_edit1(self, args=None):
        if args:
            args.update(self.args)
        else:
            args = self.args

        # show only
        new_args, error_args = check_primary_args(args, self.table_class, self.name2table, self.db_client, True)

        has_errors = len(error_args) > 0
        assert not has_errors

        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        filter_dict = {}
        for col in columns:
            if col.is_primary:
                filter_dict[col.name] = new_args[col.name]

        filter_dict['uid'] = self.my_uid
        reload_record = self.db_client.select_one(self.table_class, **filter_dict)
        return self.output_edit(reload_record, new_args, error_args, '', '')

    def output_edit2(self):
        # edit only
        new_args, error_args = check_create_args(self.args, self.table_class, self.name2table, self.db_client, True)
        has_errors = len(error_args) > 0
        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        error_msg = ''
        filter_dict = {}
        update_dict = {}
        if not has_errors:
            for col in columns:
                if col.is_primary:
                    filter_dict[col.name] = new_args[col.name]
                else:
                    update_dict[col.name] = new_args[col.name]

            filter_dict['uid'] = self.my_uid
            try:
                self.db_client.do_update(self.table_class, filter_dict, update_dict)
            except Exception, ex:
                error_msg = str('update failed')
                has_errors = True

        reload_record = None
        #if not is_edit and not has_errors:
        if not has_errors:
            filter_dict['uid'] = self.my_uid
            reload_record = self.db_client.select_one(self.table_class, **filter_dict)

        if has_errors:
            op_tips = gen_op_tips('Edit Failed! %s'%error_msg)
        else:
            op_tips = gen_op_tips('Edit Success!', True)

        return self.output_edit(reload_record, new_args, error_args, None, op_tips)


    def output_edit(self, reload_record, new_args, error_args, custom_tips=None, op_tips=None):
        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]
        ret_dict = {}
        ret_dict['list_url'] = self.list_url
        ret_dict['op_tips'] = op_tips
        ret_dict['hidden_fields'] = []
        ret_dict['fields'] = []
        ret_dict['country_config'] = country_config.COUNTRY_NAME_LIST

        filter_cols = ['uid']

        for col in columns:
            if not col.is_primary:
                continue
            col_name = col.name
            d = {}
            d['name'] = col_name
            if reload_record:
                d['value'] = getattr(reload_record, col_name)
            else:
                d['value'] = new_args.get(col_name, '')
            ret_dict['hidden_fields'].append(d)

        def chunkstring(string, length):
            return (string[0+i:length+i] for i in range(0, len(string), length))

        for col in columns:
            if col.is_primary:
                continue
            if col.is_foreign and col.name in filter_cols:
                continue

            col_name = col.name
            d = {}
            d['name'] = col_name
            if reload_record:
                d['value'] = getattr(reload_record, col_name)
            else:
                d['value'] = new_args.get(col_name, '')
            if custom_tips is None:
                d['tips'] = gen_tips() if col_name in error_args else ''
            else:
                d['tips'] = custom_tips
            d['is_normal'] = col.is_normal
            d['is_multi'] = col.is_multi
            d['is_textarea'] = col.is_textarea
            d['is_disable'] = col.is_disable
            if col.is_foreign and col.name not in filter_cols:
                options = self.get_options(col.foreign_source_key, 'name')
                d['items'] = options.items()
            if col.is_multi:
                options = self.get_multi_options(col.multi_table, col.multi_id, 'name')
                d['items'] = options.items()
                values = d['value'].split(',')
                d['selected_items'] = ','.join(('"%s"'%v for v in values))
            if col.is_textarea:
                v = d['value']
                v = v.replace('\r\n', '<caonima/>')
                v = v.replace('\n', '<caonima/>')
                import re
                v = re.sub("<!--.*?-->", "", v)
                v = v.replace('<caonima/>', '\n')
                new_items = []
                is_first = True
                for item in v.split('</script>'):
                    if not is_first:
                        new_items.append(u'<')
                        new_items.append(u'/')
                        new_items.append(u'script')
                        new_items.append(u'>')
                        new_items.append(item)
                    else:
                        new_items.append(item)
                        is_first = False
                d['value'] = new_items
            ret_dict['fields'].append(d)

        render = Render('Mobitx Edit %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.edit_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

class ModelView(object):
    def __init__(self, table_class, session_info):
        self.args = get_request_args()
        self.table_class =  table_class
        self.tmpl_reader = global_vars.tmpl_reader
        self.db_client = DBSet.get_db_client()
        self.session_info = session_info
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table

        url_name = self.table_class.__tablename__.replace('_', '').lower()
        self.list_url = get_model_uri(self.table_class, 'list')
        self.edit_url = get_model_uri(self.table_class, 'edit')
        self.create_url = get_model_uri(self.table_class, 'create')
        self.del_url = get_model_uri(self.table_class, 'del')

        self.list_tmpl = '%s_list.tmpl'%self.table_class.__tablename__
        self.create_tmpl = '%s_create.tmpl'%self.table_class.__tablename__
        self.edit_tmpl = '%s_edit.tmpl'%self.table_class.__tablename__

        self.list_tmpl = 'model_list.tmpl'
        self.create_tmpl = 'model_create.tmpl'
        self.edit_tmpl = 'model_edit.tmpl'

        self.username = session_info['username']
        self.my_uid = self.username2uid(self.username)
        self.args['uid'] = self.my_uid

    def username2uid(self, username):
        from db_client import User
        user = self.db_client.select_one(User, name=username)
        return user.id

    def get_user_by_uid(self, uid):
        from db_client import User
        user = self.db_client.select_one(User, id=uid)
        return user

    def check_permission(self, permission_type, permission):
        from db_client import User
        user = self.db_client.select_one(User, id=self.my_uid)
        user_permission = user.permission
        return check_permission(permission_type, user_permission, permission)

    def output_list(self):
        # select all by sorting
        sort_arg = self.args.get('sort')
        if sort_arg is None:
            rows = self.db_client.select_all(self.table_class, uid=self.my_uid)
        else:
            idx = int(sort_arg)
            sort_arg = get_columns(self.table_class)[idx].asc()
            rows = self.db_client.select_all_sort(self.table_class, sort_arg, uid=self.my_uid)

        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        filter_cols = ['uid']

        field_names = []
        for col in columns:
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
                            tmp_records[column.name] = (getattr(row, column.name))

                if column.is_foreign and column.name not in filter_cols:
                    source_col = column.foreign_source_key
                    options = self.get_options(source_col, 'name')
                    _fid = getattr(row, column.name)
                    v = options.get(_fid, 'UNKNOWN')
                    tmp_records[column.name] = (v)

            obj_info = {}
            obj_info['values'] = tmp_records
            obj_info['edit_url'] = make_url(self.edit_url, {'url' : request.path, 'id' : pk_id})
            obj_info['id'] = pk_id
            records.append(obj_info)
        d = {
            'cur_url' : request.path,
            'create_url' : make_url(self.create_url, {'url' : request.path}),
            'del_url' : self.del_url,
            'field_names' : field_names,
            'records' : records,
        }

        title = '2Fly %s List'%self.table_class.__name__
        render = Render(title, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.list_tmpl)
        body_str = Template(body_tmpl).render(**d)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})


    def output_create1(self):
        return self.output_create(False, '', '')

    def output_create2(self):
        return self.output_create(True)


    def output_create(self, is_create, custom_tips=None, custom_op_tips=None):
        new_args, error_args = check_create_args(self.args, self.table_class, self.name2table, self.db_client)
        has_errors = len(error_args) > 0
        err_msg = ''

        if not has_errors and is_create:
            model = self.table_class(**new_args)
            try:
                self.db_client.do_save(model)
            except Exception, ex:
                has_errors = True
                err_msg += str(ex)

        if has_errors:
            op_tips = gen_op_tips('Create Failed! %s'%err_msg)
        else:
            op_tips = gen_op_tips('Create Success!', True)
        #op_tips = '''<div class="alert alert-success"><strong>Create Success!</strong></div>'''

        if custom_op_tips is not None:
            op_tips = custom_op_tips

        ret_dict = {}
        ret_dict['list_url'] = self.list_url
        ret_dict['op_tips'] = op_tips
        ret_dict['fields'] = []
        ret_dict['country_config'] = country_config.COUNTRY_NAME_LIST

        filter_cols = ['uid']
        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]
        for col in columns:
            if col.is_primary:
                continue
            if col.is_foreign and col.name in filter_cols:
                continue

            d = {}
            d['name'] = col.name
            if custom_tips is None:
                d['tips'] = gen_tips() if col.name in error_args else ''
            else:
                d['tips'] = custom_tips
            d['is_normal'] = col.is_normal
            d['is_multi'] = col.is_multi
            d['is_textarea'] = col.is_textarea
            d['is_disable'] = col.is_disable
            if col.is_foreign and col.name not in filter_cols:
                source_col = col.foreign_source_key
                options = self.get_options(source_col, 'name')
                d['items'] = options.items()
            if col.is_multi:
                options = self.get_multi_options(col.multi_table, col.multi_id, 'name')
                d['items'] = options.items()
            if col.is_disable:
                uri = '/%s/%s'%(self.my_uid, gen_uuid())
                d['disable_value'] = uri
            ret_dict['fields'].append(d)

        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.create_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def output_edit1(self):
        # show only
        new_args, error_args = check_primary_args(self.args, self.table_class, self.name2table, self.db_client, True)

        has_errors = len(error_args) > 0
        assert not has_errors

        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        filter_dict = {}
        for col in columns:
            if col.is_primary:
                filter_dict[col.name] = new_args[col.name]

        filter_dict['uid'] = self.my_uid
        reload_record = self.db_client.select_one(self.table_class, **filter_dict)
        return self.output_edit(reload_record, new_args, error_args, '', '')



    def output_edit2(self):
        # edit only
        new_args, error_args = check_create_args(self.args, self.table_class, self.name2table, self.db_client, True)
        has_errors = len(error_args) > 0
        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        error_msg = ''
        filter_dict = {}
        update_dict = {}
        if not has_errors:
            for col in columns:
                if col.is_primary:
                    filter_dict[col.name] = new_args[col.name]
                else:
                    update_dict[col.name] = new_args[col.name]

            filter_dict['uid'] = self.my_uid
            try:
                self.db_client.do_update(self.table_class, filter_dict, update_dict)
            except Exception, ex:
                error_msg = str('update failed')
                has_errors = True

        reload_record = None
        #if not is_edit and not has_errors:
        if not has_errors:
            filter_dict['uid'] = self.my_uid
            reload_record = self.db_client.select_one(self.table_class, **filter_dict)

        if has_errors:
            op_tips = gen_op_tips('Edit Failed! %s'%error_msg)
        else:
            op_tips = gen_op_tips('Edit Success!', True)

        return self.output_edit(reload_record, new_args, error_args, None, op_tips)

    def output_edit(self, reload_record, new_args, error_args, custom_tips=None, op_tips=None):
        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]
        ret_dict = {}
        ret_dict['list_url'] = self.list_url
        ret_dict['op_tips'] = op_tips
        ret_dict['hidden_fields'] = []
        ret_dict['fields'] = []
        ret_dict['country_config'] = country_config.COUNTRY_NAME_LIST

        filter_cols = ['uid']

        for col in columns:
            if not col.is_primary:
                continue
            col_name = col.name
            d = {}
            d['name'] = col_name
            if reload_record:
                d['value'] = getattr(reload_record, col_name)
            else:
                d['value'] = new_args.get(col_name, '')
            ret_dict['hidden_fields'].append(d)

        def chunkstring(string, length):
            return (string[0+i:length+i] for i in range(0, len(string), length))

        for col in columns:
            if col.is_primary:
                continue
            if col.is_foreign and col.name in filter_cols:
                continue

            col_name = col.name
            d = {}
            d['name'] = col_name
            if reload_record:
                d['value'] = getattr(reload_record, col_name)
            else:
                d['value'] = new_args.get(col_name, '')
            if custom_tips is None:
                d['tips'] = gen_tips() if col_name in error_args else ''
            else:
                d['tips'] = custom_tips
            d['is_normal'] = col.is_normal
            d['is_multi'] = col.is_multi
            d['is_textarea'] = col.is_textarea
            d['is_disable'] = col.is_disable
            if col.is_foreign and col.name not in filter_cols:
                options = self.get_options(col.foreign_source_key, 'name')
                d['items'] = options.items()
            if col.is_multi:
                options = self.get_multi_options(col.multi_table, col.multi_id, 'name')
                d['items'] = options.items()
                values = d['value'].split(',')
                d['selected_items'] = ','.join(('"%s"'%v for v in values))
            if col.is_textarea:
                v = d['value']
                v = v.replace('\r\n', '<caonima/>')
                v = v.replace('\n', '<caonima/>')
                import re
                v = re.sub("<!--.*?-->", "", v)
                v = v.replace('<caonima/>', '\n')
                new_items = []
                is_first = True
                for item in v.split('</script>'):
                    if not is_first:
                        new_items.append(u'<')
                        new_items.append(u'/')
                        new_items.append(u'script')
                        new_items.append(u'>')
                        new_items.append(item)
                    else:
                        new_items.append(item)
                        is_first = False
                d['value'] = new_items
            ret_dict['fields'].append(d)

        render = Render('Mobitx Edit %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.edit_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})



    def get_options(self, foreign_source_key, tag_name):
        table_name = foreign_source_key.target_fullname.split('.')[0]
        pk_name = foreign_source_key.target_fullname.split('.')[1]
        tb_class = self.name2table.get(table_name)
        records = self.db_client.iter_all(tb_class, uid=self.my_uid)
        ret_dict = {}
        for record in records:
            ret_dict[getattr(record, pk_name)] = getattr(record, tag_name)

        return ret_dict

    def get_multi_options(self, table_class, pk_name, tag_name):
        table_name = table_class.__tablename__
        tb_class = self.name2table.get(table_name)
        records = self.db_client.iter_all(tb_class, uid=self.my_uid)
        ret_dict = {}
        for record in records:
            ret_dict[getattr(record, pk_name)] = getattr(record, tag_name)

        return ret_dict

    def check_is_massival_inner_user(self):
        user = self.get_user_by_uid(self.my_uid)
        return check_is_massival_inner_user(user.permission)

    def get_admin_config(self, table_class):
        records = self.db_client.iter_all(table_class, uid=SUPER_ADMIN_UID)
        return records

def check_create_args(args, table_class, name2table, db_client, check_primary=False):
    normal_columns = get_normal_columns(table_class)
    foreign_columns = get_foreign_keys(table_class)
    foreign_source_columns = get_foreign_source_keys(table_class)
    if check_primary:
        primary_columns = get_primary_keys(table_class)
    else:
        primary_columns = []

    error_args = {}
    new_args = {}
    for col in normal_columns:
        value = args.get(col.name)
        if value is None:
            if col.name in view_util.nullable_field:
                continue
            else:
                error_args[col.name] = 'miss'
                continue

        if type(col.type) == String:
            if col.default is None and value is None:
                error_args[col.name] = 'miss'
            new_args[col.name] = value.strip()
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
    for i in xrange(len(foreign_columns)):
        col = foreign_columns[i]
        value = args.get(col.name)
        if value is None:
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
        tb_class = name2table.get(table_name)
        records = db_client.select_all(tb_class, **d)
        if not records:
            error_args[col.name] = 'select'


    for i in xrange(len(primary_columns)):
        col = primary_columns[i]
        value = args.get(col.name)
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
        records = db_client.select_all(table_class, **d)
        if not records:
            error_args[col.name] = 'select'

    return new_args, error_args


# check primary_args is existed or not
def check_primary_args(args, table_class, name2table, db_client, check_primary=False):
    if check_primary:
        primary_columns = get_primary_keys(table_class)
    else:
        primary_columns = []

    error_args = {}
    new_args = {}

    for i in xrange(len(primary_columns)):
        col = primary_columns[i]
        value = args.get(col.name)
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
        records = db_client.select_all(table_class, **d)
        if not records:
            error_args[col.name] = 'select'

    return new_args, error_args




