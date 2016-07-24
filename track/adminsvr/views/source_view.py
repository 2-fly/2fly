 #!/usr/bin/env python
# -*-coding:utf-8 -*-

import global_vars
import view_util
from sqlalchemy import Integer, String, Float
from mako.template import Template
from view import Render, ModelView
from db_client import TrafficSource, AdminTrafficSource, get_normal_columns
from flask import redirect
from utils import to_links

class SourceView(ModelView):
    def __init__(self, session_info):
        self.table_class = TrafficSource
        self.tmpl_reader = global_vars.tmpl_reader
        self.source_tmpl = "source.tmpl"
        self.db_client = global_vars.global_db_set.get_db_client()
        self.session_info = session_info
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.args = view_util.get_request_args()
        self.args['uid'] = self.my_uid
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table

    def get_source_field(self):
        try:
            sid = int(self.args.get("source_id"))
        except Exception:
            sid = 0
        ret = ""
        if sid:
            model = self.db_client.select_one(self.table_class, id=sid)
            ret = model.fields
        return ret

    def check_args(self, is_create=False):
        error = {}
        ret = True
        if not is_create:
            self.args['id'] = int(self.args['id'])
        self.args['uid'] = self.my_uid
        for col in get_normal_columns(self.table_class):
            value = self.args.get(col.name)
            error[col.name] = ""
            if type(col.type) == String:
                if col.default is None and value is None:
                    ret = False
                    error[col.name] = view_util.gen_tips()
                    continue
            elif type(col.type) == Integer:
                if col.default is None and value is None:
                    ret = False
                    error[col.name] = view_util.gen_tips()
                    continue
                else:
                    try:
                        self.args[col.name] = int(value)
                    except Exception:
                        error[col.name] = view_util.gen_tips()
                        continue
                if value:
                    self.args[col.name] = int(value)
        return ret, error

    def output_edit(self, save=False):
        ret_dict = {'list_url':global_vars.URL_TS_LIST, 'op_tips':"", 'tips':{}}
        return self._do_output_edit(ret_dict, save)

    def _do_output_edit(self, ret_dict=None, save=False):
        ret_dict = ret_dict or {}
        if save:
            new_ret, error_args = view_util.check_create_args(self.args, self.table_class, self.name2table, self.db_client, check_primary=True)
            source = self.table_class(**view_util.filter_model_key(self.table_class, new_ret))
            if not error_args:
                if self.db_client.do_save(source):
                    ret_dict['op_tips'] = view_util.gen_op_tips("Edit Success!", True)
                else:
                    ret_dict['op_tips'] = view_util.gen_op_tips("Edit Failed!", False)
            else:
                ret_dict['op_tips'] = view_util.gen_op_tips("Edit Failed!", False)
                for k, v in error_args.items():
                    ret_dict['op_tips'] = view_util.gen_op_tips("Create Failed!", False)
                    ret_dict['tips'][k] = view_util.gen_tips()
        else:
            if self.args.get('create'):
                ret_dict['op_tips'] = view_util.gen_op_tips("Create Success!", True)
            source = self.db_client.select_one(self.table_class, id=self.args['id'])
        ret_dict['timezone'] = source.timezone
        ret_dict['id'] = source.id
        ret_dict['fields'] = source.fields
        ret_dict['ad_server_domains'] = source.ad_server_domains
        ret_dict['name'] = source.name
        ret_dict['postback_url'] = source.postback_url
        ret_dict['title'] = 'Edit'

        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.source_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def output_create(self, save=False):
        ret_dict = {'list_url':global_vars.URL_TS_LIST, 'edit_url':global_vars.URL_TS_EDIT, 'op_tips':"", 'tips':{}}
        return self._do_output_create(ret_dict, save)

    def _do_output_create(self, ret_dict=None, save=False):
        ret_dict = ret_dict or {}
        if save:
            new_ret, error_args = view_util.check_create_args(self.args, self.table_class, self.name2table, self.db_client, check_primary=False)
            source = self.table_class(**view_util.filter_model_key(self.table_class, new_ret))
            if not error_args:
                if self.db_client.add_one(source):
                    ret_dict['op_tips'] = view_util.gen_op_tips("Create Success!", True)
                    return redirect("%s?id=%d&create=1"%(ret_dict.get('edit_url', ""), source.id))
                else:
                    ret_dict.update(self.args)
                    ret_dict['op_tips'] = view_util.gen_op_tips("Create Failed!", False)
            else:
                ret_dict.update(self.args)
                for k, v in error_args.items():
                    ret_dict['op_tips'] = view_util.gen_op_tips("Create Failed!", False)
                    ret_dict['tips'][k] = view_util.gen_tips()

        ret_dict['title'] = 'Create'

        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.source_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})


class AdminSourceView(SourceView):
    def __init__(self, session_info):
        super(AdminSourceView, self).__init__(session_info)
        self.table_class = AdminTrafficSource

    def output_edit(self, save=False):
        ret_dict = {'list_url':global_vars.URL_ADMIN_TS_LIST, 'op_tips':"", 'tips':{}}
        return self._do_output_edit(ret_dict, save)
    
    def output_create(self, save=False):
        ret_dict = {'list_url':global_vars.URL_ADMIN_TS_LIST, 'edit_url':global_vars.URL_ADMIN_TS_EDIT, 'op_tips':"", 'tips':{}}
        return self._do_output_create(ret_dict, save)

