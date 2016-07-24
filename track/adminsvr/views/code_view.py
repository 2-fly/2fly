#!/usr/bin/env python
# -*-coding:utf-8 -*-

import ujson
import datetime
import view_util
import global_vars

from sqlalchemy import Integer, String, Float
from mako.template import Template
from view import ModelView, Render, BaseColumn 
from global_vars import global_db_set as DBSet 
from static_result import decrypt, encrypt
from utils import to_links_custom


class CodeView(ModelView):
    def __init__(self, session_info):
        self.decrypt_tmpl = "decrypt.tmpl"
        self.db_client = DBSet.get_db_client()
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.table_name = "Decrypt"
        self.tmpl_reader = global_vars.tmpl_reader
        self.session_info = session_info
        #self.check_relative_uid(self.my_uid)

    def output_edit(self, encrypt_str=None, decrypt_str=None, op=None):
        ret_dict = {
            "encrypt" : "",
            "decrypt" : "",
        }
        if op == "encrypt":
            ret_dict= self.encrypt(decrypt_str)
        elif op == "decrypt":
            ret_dict = self.decrypt(encrypt_str)
        return self._render(ret_dict)

    def encrypt(self, decrypt_str=None):
        decrypt_str = decrypt_str or ""
        _list = decrypt_str.split("\r\n")
        result = []
        for de in _list:
            de = de.encode('utf-8')
            try:
                en = encrypt(de)
                en = en.encode('utf-8')
                result.append(en)
            except Exception, ex:
                print ex
                s = "decrypt error: %s" % (de)
                result.append(s)

        
        encrypt_str = "\r\n".join(result)
        ret_dict = {
            "encrypt" : encrypt_str,
            "decrypt" : decrypt_str,
        }
        return ret_dict

    def decrypt(self, encrypt_str=None):
        encrypt_str = encrypt_str or ""
        _list = encrypt_str.split("\r\n")
        result = []
        for en in _list:
            en = en.encode('utf-8')
            try:
                de = decrypt(en)
                de = de.encode('utf-8')
                result.append(de)
            except Exception, ex:
                print ex
                s = "decrypt error: %s" % (en)
                result.append(s)

        
        decrypt_str = "\r\n".join(result)
        ret_dict = {
            "encrypt" : encrypt_str,
            "decrypt" : decrypt_str,
        }
        return ret_dict

    def _render(self, ret_dict=None):
        ret_dict = ret_dict or {"encrypt" : "", "decrypt" : ""}
        render = Render('Massival decrypt%s'%self.table_name, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(self.decrypt_tmpl)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links_custom(self.table_name, 'list')})

