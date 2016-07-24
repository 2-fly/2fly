#!/usr/bin/env python
# -*- coding:utf-8 -*-
from mako.template import Template
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Sequence, Float, Text, SmallInteger

import init_env

from utils import get_model_uri
from db_client import get_normal_columns, get_foreign_keys, get_foreign_source_keys, get_primary_keys
import global_vars
import settings

def gen_op_tips(tips, success=False):
    if not success:
        return '''<p class="bg-class bg-danger"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></p>'''%tips
    else:
        return '''<p class="bg-class bg-success text-success"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></p>'''%tips


def gen_tips():
    return '''<div><span class="label label-important">Field Is Required</span></div>'''



def to_links(url, t):
    new_links = []
    t = int(t)
    for item in global_vars.total_links:
        if 'limit' in item and item['limit'] != t:
            continue
        tmp_links = []
        for i in item['items']:
            found = False
            if url and 'tag' in i and url.find(i['tag']) != -1:
                found = True
            i['act'] = found
            tmp_links.append(i)
        found = False
        if url and 'tag' in item and url.find(item['tag']) != -1:
            found = True
        new_links.append({'name':item['name'], 'items':tmp_links, 'img':item['img'], 'href':item.get('href'), 'act':found})
    return new_links

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

    def gen_output(self, body_str, tmpl_dict=None):
        index_tmpl = self.tmpl_reader.read_file(self.tmpls['index'])
        header_tmpl = self.tmpl_reader.read_file(self.tmpls['header'])
        #footer_tmpl = self.tmpl_reader.read_file(self.tmpls['footer'])
        navtop_tmpl = self.tmpl_reader.read_file(self.tmpls['nav_top'])
        navleft_tmpl = self.tmpl_reader.read_file(self.tmpls['nav_left'])

        d = {
            'title' : self.title, 'version' : settings.version
        }
        header_str = Template(header_tmpl).render(**d)

        if tmpl_dict is None:
            tmpl_dict = {}

        d = {
            'header' : header_str,
            'nav_top' : Template(navtop_tmpl).render(username=self.session_info['username'], logout=global_vars.URL_LOGOUT, edit_account=global_vars.URL_MODIFY_USER),
            'nav_left' : Template(navleft_tmpl).render(**tmpl_dict),
            'body' : body_str,
        }
        index_str = Template(index_tmpl).render(**d)
        return index_str

def init_tmpl_dict():
    return {"version":settings.version}

def username2uid(username, user_type, dbclient):
    from db_client import Publisher, Advertiser
    cls = Publisher if int(user_type) == global_vars.PUBLISHER else Advertiser
    user = dbclient.select_one(cls, name=username)
    return user.id

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
            if col.nullable:
                continue
            else:
                error_args[col.name] = 'miss'
                continue

        if type(col.type) in (String, Text):
            if col.default is None and not value:
                error_args[col.name] = 'miss'
            new_args[col.name] = value.strip()
        elif type(col.type) in (Integer, SmallInteger):
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
        if col.unique and col.name not in error_args and not check_primary:
            if db_client.select_one(table_class, **{col.name: new_args[col.name]}):
                error_args[col.name] = 'unique'


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

def get_foreign_key_options(db, cls, name, **d):
    return [[i.id, getattr(i, name)] for i in db.select_all(cls, **d)]
