#!/usr/bin/env python
# -*- coding:utf-8 -*-

import locale
import urllib
import smtplib
import string
import settings
import global_vars
from os import path as osp
from functools import wraps
from email.mime.text import MIMEText
from flask import request, current_app
from tools.permission import PermissionType
from db_client import User
from config.permission_config import PERMISSION_IGNORE

locale.setlocale(locale.LC_ALL, "en_US")

support_new_decode = True
try:
    a = ''.decode('utf-8', errors='ignore')
except Exception:
    support_new_decode = False

def encode_from_utf8(s):
    if support_new_decode:
        return s.encode("utf-8", errors="ignore")
    else:
        return s.encode("utf-8")

def decode_from_utf8(s):
    if support_new_decode:
        return s.decode("utf-8", errors="ignore")
    else:
        return s.decode("utf-8")

def format_int_comma(v, args=None):
    return locale.format("%d", v, grouping=True)

def format_float_comma(v, args=None):
    return locale.format("%.2f", v, grouping=True)

def format_str(v, args=None):
    return locale.format("%s", v, grouping=True)

def check_is_massival_inner_user(permission):
    pt = PermissionType()
    ins = pt.get(permission)
    obj = ins()
    return obj.check_is_massival_inner_user()

def check_permission(permission_type, user_permission, permission):
    pt = PermissionType()
    ins = pt.get(user_permission)
    obj = ins()
    return obj.check_permission(permission_type, permission)

def get_user_from_request():
    from global_vars import global_db_set as DBSet
    username = request.cookies.get("username", None)
    user = DBSet.get_db_client().select_one(User, name=username)
    return user

def _to_links(uri_name, op=None):
    user = get_user_from_request()
    pt = PermissionType()
    ins = pt.get(user.permission)
    permissionObj = ins()
    links = []
    if permissionObj is None:
        return links
    for item in global_vars.total_links:
        tmp_links = []
        p = item['permission']
        nav = False
        if len(item['items']) == 0:
            if not permissionObj.check_permission(p, 1):
                continue
            nav = True
        else:
            for k, v, per in item['items']:
                if p != PERMISSION_IGNORE and not permissionObj.check_permission(p, per):
                    continue
                found = False
                nav = True
                if v == uri_name or k == uri_name:
                    found = True
                tmp_links.append((k, v, found))
        if nav or p == PERMISSION_IGNORE:
            links.append({'name':item['name'], 'items':tmp_links, 'img':item['img'], 'href':item.get('href')})
    return links

def to_links(table_class, op=None):
    uri_name = get_model_uri(table_class, op)
    return _to_links(uri_name, op)

def to_links_custom(table_name, op=None):
    return _to_links(table_name, op)

def read_file(path):
    with open(path, 'r') as f:
        return f.read()


def get_model_uri(table_class, op=None):
    if type(table_class) == str:
        uri = [table_class, op] if op is not None else [table_class]
        return "/%s"%("/".join(uri))
    else:
        uri_name = table_class.__tablename__.replace('_', '').lower()
        return '/admin/%s/%s'%(uri_name, op)


def get_normal_uri(uri):
    return '/admin%s'%uri


def make_url(url_path, params=None):
    if params is None:
        ec_params = ''
        url = url_path
    else:
        ec_params = urllib.urlencode(params)
        url = '%s?%s' % (url_path, ec_params)
    return url
    #urllib.quote


class TemplateReader(object):
    def __init__(self, directory):
        self.directory = directory

    def read_file(self, path):
        with open(osp.join(self.directory, path), 'r') as f:
            s = f.read()
            return s.decode('utf8')


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            res = func(*args, **kwargs)
            data = str(res.data) if type(res) != str else res
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function

def do_send_mail(to_list, sender, subject, content, my_email):
    me = my_email
    msg = MIMEText(content,_subtype='html',_charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ",".join(to_list)
    msg['Reply-To'] = 'noreply@%s'%settings.mail_postfix
    msg['List-Unsubscribe'] = '<mailto:unsubscribe@%s>'%settings.mail_postfix
    msg['From-Name'] = sender
    msg['From-Domain'] = settings.mail_postfix
    msg['From-Address'] = 'noreply@%s'%settings.mail_postfix

    try:
        s = smtplib.SMTP()
        s.connect(settings.mail_host)
        s.starttls()
        s.login(settings.mail_user,settings.mail_pwd)
        s.sendmail(me, to_list, msg.as_string())
        s.close()
        return True, None
    except Exception, e:
        print e
        return False, e

def send_mail(to_list, url, user_name):
    sender = 'Massival'
    subject = 'massival register'
    content = '<p>You recently entered a new email address for <b>%s</b>.</p><p>Please confirm your email by click <a href="%s">here</a>.</p>'%(user_name, url)
    #me = sender+"<"+settings.mail_user+"@"+settings.mail_postfix+">"
    to_list = [to_list]
    me = '%s<%s@%s>'%(sender, settings.mail_sender, settings.mail_postfix)
    return do_send_mail(to_list, sender, subject, content, me)


