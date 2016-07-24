#!/usr/bin/env python
# -*-coding:utf-8 -*-
from utils import get_model_uri, make_url, to_links, encode_from_utf8, decode_from_utf8
from sqlalchemy import Integer, String, Float
from mako.template import Template
from db_client import LandingPage
from view import ModelView, Render, BaseColumn 
from flask import redirect, request
from view import check_create_args, gen_op_tips

import global_vars
import view_util
import ujson

__ALLOW_FILES = ['html']
def allow_file(filename):
    return '.' in filename and \
               filename.rsplit('.', 1)[1] in __ALLOW_FILES

class LanderView(ModelView):
    def __init__(self, session_info):
        self.table_class = LandingPage
        self.session_info = session_info
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table

        self.db_client = global_vars.global_db_set.get_db_client()
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.args = view_util.get_request_args()
        self.args['uid'] = self.my_uid
        self.tmpl_reader = global_vars.tmpl_reader

    def set_hidden(self):
        ids = self.args['ids']
        back = self.args['back']
        t = int(self.args['type'])

        assert t in [1, 0]

        ids = [int(i) for i in ids.split(",")]
        for i in ids:
            camp = self.db_client.select_one(LandingPage, id=i)
            if camp:
                camp.hidden = t
                self.db_client.do_save(camp)

        return redirect(back)

    def output_list(self):
        rows = self.db_client.iter_all(self.table_class, uid=self.my_uid)

        columns = [BaseColumn(col, self.table_class) for col in self.table_class.__table__.columns]

        filter_cols = ['uid']
        name_filter = ['uid', 'hidden', 'source', 'page_source', 'lander_link']
        name_filter2 = ['source']

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

            if col.is_foreign and col.name not in  name_filter:
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

                if column.is_normal and column.name not in name_filter2:
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
            obj_info['edit_url'] = make_url(global_vars.URL_LP_EDIT, {'url' : request.path, 'id' : pk_id})
            obj_info['id'] = pk_id
            records.append(obj_info)

        d = {
            'cur_url' : request.path,
            'create_url' : make_url(global_vars.URL_LP_CREATE, {'url' : request.path}),
            #'del_url' : self.del_url,
            'field_names' : field_names,
            'campaign_check_url' : global_vars.URL_CHECK_CAMPAIGN,
            'records' : records,
            'set_hidden_url' : global_vars.URL_LP_SET_HIDDEN,
            'batch_upload_url' : global_vars.URL_LP_BATCH_UPLOAD,
        }

        title = 'Massival %s List'%self.table_class.__name__
        render = Render(title, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file('toolbar_model_list.tmpl')
        body_str = Template(body_tmpl).render(**d)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def _read_upload_files(self):
        upload_files = request.files.getlist("upload_files")
        source_list = []
        err = ""
        for file in upload_files:
            if not allow_file(file.filename):
                err = "%s %s is uploaded fail. only allow upload html file." % (err, file.filename)
                continue
            source = ""
            for line in file.stream:
                source = "%s%s" % (source, line)
            source = decode_from_utf8(source)
            source = encode_from_utf8(source)
            info = (file.filename, source)
            source_list.append(info)
        return dict(ok=True, err=err, source_list=source_list)

    def _create_landerpage(self, name, source):
        args = dict(
            uid = self.my_uid,
            page_source = '',
            source = source,
            name = name,
            lander_mode = 0,
            lander_link = "",
        )
        new_args, error_args = check_create_args(args, self.table_class, self.name2table, self.db_client)
        has_errors = len(error_args) > 0
        err_msg = ''

        if not has_errors:
            model = self.table_class(**new_args)
            try:
                self.db_client.do_save(model)
            except Exception, ex:
                has_errors = True
                err_msg += str(ex)
        else:
            err_msg = "%s saved fail.\n" % name
        return err_msg

    def output_batch_upload(self):
        tips = None 
        result = self._read_upload_files()
        if result["ok"]:
            err = result["err"]
            create_err = ""
            for info in result["source_list"]:
                name, source = info
                create_err = "%s%s" % (create_err, self._create_landerpage(name, source))

            err = "%s%s" % (err, create_err)
            ok = None 
            is_show_tips = True
            if len(result["source_list"]) > 0:
                if err == "":
                    ok = True
                    err = "upload successed."
                else:
                    ok = False
            else:
                if err != "":
                    ok = False
            if ok is not None:
                tips = gen_op_tips(err, ok)
        else:
            tips = gen_op_tips(result["err"], False)
        return self.output_batch_upload_html(tips)

    def output_batch_upload_html(self, tips=None):
        d = {
            'list_url' : make_url(global_vars.URL_LP_LIST, {'url' : request.path}),
            'create_url' : make_url(global_vars.URL_LP_CREATE, {'url' : request.path}),
            'tips' : tips or "",
        }
        title = 'Massival %s batch upload' % self.table_class.__name__
        render = Render(title, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file('landingpage_batchupload.tmpl')
        body_str = Template(body_tmpl).render(**d)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

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
                has_errors = True
                err_msg += str(ex)
                json_dict = {'ret':'fail', 'msg': ex}
        else:
            json_dict = {'ret':'fail'}
        return ujson.dumps(json_dict)
