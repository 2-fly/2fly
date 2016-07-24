#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib
import hashlib
import time
from os import path as osp
from functools import wraps

import smtplib
from email.mime.text import MIMEText
from flask import request, current_app
import settings

timezone_offset = -time.timezone
TIMEZONE = timezone_offset / 3600
ONE_DAY_SECONDS = 3600 * 24

support_new_decode = True
try:
    a = ''.decode('utf-8', errors='ignore')
except Exception:
    support_new_decode = False

def decode_from_utf8(s):
    if support_new_decode:
        return s.decode("utf-8", errors="ignore")
    else:
        return s.decode("utf-8")

def gen_secret(passwd):
    return hashlib.md5(passwd + '_' + settings.app_secret).hexdigest()

def gen_md5(s):
    return hashlib.md5(s).hexdigest()

def gen_skey(username, password, time_str):
    s = '%s_%s_%s'%(username, password, time_str)
    return hashlib.md5(s).hexdigest()


def get_request_args():
    d1 = request.args.to_dict()
    d2 = request.form.to_dict()
    d3 = request.files.to_dict()
    d1.update(d2)
    d1.update(d3)
    return d1

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def get_model_name(table_class):
    return table_class.__tablename__.replace('_', '').lower()

def get_model_uri(table_class, op=None):
    if type(table_class) == str:
        uri = [table_class, op] if op is not None else [table_class]
        return "/%s"%("/".join(uri))
    else:
        uri_name = table_class.__tablename__.replace('_', '').lower()
        return '/poponads/%s/%s'%(uri_name, op)


def get_normal_uri(uri):
    return '/poponads%s'%uri


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

def send_mail(to_list, url, user_name):
    to_list = [to_list]
    sender = 'Massival'
    subject = 'massival register'
    content = '<p>You recently entered a new email address for <b>%s</b>.</p><p>Please confirm your email by click <a href="%s">here</a>.</p>'%(user_name, url)
    #me = sender+"<"+settings.mail_user+"@"+settings.mail_postfix+">"
    me = '%s<%s@%s>'%(sender, settings.mail_sender, settings.mail_postfix)

    msg = MIMEText(content,_subtype='html',_charset='utf-8')
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ";".join(to_list)
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
        return False, e
