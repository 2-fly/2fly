#!/usr/bin/env python
# -*-coding:utf-8 -*-
from sqlalchemy import Integer, String, Float, Text
from flask import request
from db_client import get_normal_columns, get_primary_keys, get_foreign_source_keys, get_foreign_keys, get_nonprimary_columns, get_columns
import uuid
import global_vars
from config.permission_config import *

nullable_field = ['hidden']

def gen_op_tips(tips, success=False):
    if not success:
        return '''<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></div>'''%tips
    else:
        return '''<div class="alert alert-success"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></div>'''%tips

def gen_tips():
    return '<span class="label label-important" style="margin-left:20px">field is error!</span>'

def gen_direct_offer_tips():
    return '<span class="label label-important" style="margin-left:20px">payout has changed.please refresh page!</span>'

def gen_direct_offer_change_tips(payout):
    return '<span class="label label-important" style="margin-left:20px">payout has changed to %s </span>' % (payout)

def dict_append(dest, k, v):
    assert isinstance(dest, dict)
    if dest.get(k):
        dest[k].append(v)
    else:
        dest[k] = [v]

def filter_model_key(table_class, args):
    new_args = {}
    for col in table_class.__table__.columns:
        v = args.get(col.name)
        if v is not None:
            new_args[col.name] = v
    return new_args

def get_multi_table(table_class, col_name):
    from db_client import SwapRotation, Path, Offer, LandingPage

    if table_class == Path and col_name == 'offers':
        return Offer
    if table_class == Path and col_name == 'landing_pages':
        return LandingPage
    if table_class == SwapRotation and col_name == 'paths':
        return Path
    return None

def gen_uuid():
    return str(uuid.uuid4()).replace('-', '')

def username2uid(username, dbclient):
    from db_client import User
    user = dbclient.select_one(User, name=username)
    return user.id

def get_request_args():
    d1 = request.args.to_dict()
    d2 = request.form.to_dict()
    d1.update(d2)
    return d1

__TABLE_TO_ADMIN_TABLE = {
    "traffic_source" : "admin_traffic_source", 
    "affiliate_network" : "admin_affiliate_network",
    }
def get_admin_table(table_name):
    return __TABLE_TO_ADMIN_TABLE.get(table_name, table_name)

def check_create_args(args, table_class, name2table, db_client, check_primary=False, is_inner_user=False):
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
            if col.name in nullable_field:
                continue
            else:
                error_args[col.name] = 'miss'
                continue

        if type(col.type) in (String, Text):
            if col.default is None and not value:
                error_args[col.name] = 'miss'
            new_args[col.name] = value.encode("utf8")
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
        if is_inner_user:
            table_name = get_admin_table(table_name)
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


