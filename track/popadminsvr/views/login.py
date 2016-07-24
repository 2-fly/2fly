#!/usr/bin/env python
# -*- coding:utf-8 -*-
from mako.template import Template

from db_client import Publisher, Advertiser

import init_env
import global_vars

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

def login(username, password, t):
    db_client = global_vars.global_db_set.get_db_client()
    if not username or not password:
        user = None
    else:
        if t == global_vars.PUBLISHER:
            users = db_client.select_all(Publisher, name=username, password=password)
            t = global_vars.PUBLISHER
        else:
            users = db_client.select_all(Advertiser, name=username, password=password)
            t = global_vars.ADVERTISER
        user = None
        if users:
            user = users[0]

    if user:
        return True
    return False


