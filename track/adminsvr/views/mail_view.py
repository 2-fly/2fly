#!/usr/bin/env python
# -*-coding:utf-8 -*-
from view import ModelView, Render 
from utils import get_model_uri, to_links
from mako.template import Template
from config.rule_config import rule, rule_type
from tools import account_tools
from commlib.db.redis_helper import RedisHashTable2
from commlib.db.db_tabledef import virus_domains_key, virusdomains_admin_table
from user_db_client import Mail, UserMail
from db_client import User
from flask import redirect

import settings
import ujson
import time, datetime
import global_vars
import view_util
import verify_urls

MAIL_TYPE = {
    1:"系统消息",
    2:"对账单",
}

class MailView(ModelView):
    def __init__(self, session_info):
        self.tmpl_reader = global_vars.tmpl_reader
        self.table_class = Mail
        self.session_info = session_info
        self.db_client = global_vars.global_db_set.get_db_client()
        self.user_db_client = global_vars.global_db_set.get_user_db_client()
        self.redis_cli = RedisHashTable2(host=settings.redis_host, port=settings.redis_port)
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.check_relative_uid(self.my_uid)
        self.args = view_util.get_request_args()
        self.args['uid'] = self.my_uid
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table


    def _check_is_admin(self):
        user = self.db_client.select_one(User, id=self.ori_uid)
        return user.permission == 1

    def create_mail(self):
        return ""

    def get_msg_list_json(self):
        ret_list = []
        is_admin = self._check_is_admin()
        mail_list = self.user_db_client.iter_all(UserMail, uid=self.my_uid) if not is_admin else self.user_db_client.iter_all(UserMail)
        for mail_info in mail_list:
            detail = self.user_db_client.select_one(Mail, id=mail_info.mid)
            ltime = time.localtime(detail.create_time)
            timeStr=time.strftime("%Y-%m-%d %H:%M:%S", ltime)
            mail = {"id":mail_info.id, "content":detail.content, "author":detail.sender, "create_time":timeStr,"title":detail.title, 'is_read':mail_info.read}
            if is_admin:
                user = self.db_client.select_one(User, id=mail_info.uid)
                mail['username'] = user.name
            ret_list.insert(0, mail)
        ret = {"code":200, "data":ret_list}
        return ret

    def msg_list(self):
        ret_dict = {
            "req_url":global_vars.URL_GET_MSG_LIST_JSON,
            "scan_url":global_vars.URL_SCAN_MSG,
            "title":"Create",
            "create_url": global_vars.URL_SEND_MSG,
            "is_admin":self._check_is_admin(),
        }
        tmp_path = "message_list.tmpl"
        render = Render('Mobitx Create %s'%'Message', self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def send_msg(self, post=False):
        if not self._check_is_admin():
            return redirect(global_vars.URL_MSG_LIST)
        if post:
            return self.send_msg2()
        else:
            return self.send_msg1()

    def check_send_msg_args(self):
        error_args = {}
        new_ret = {"create_time":int(time.time())}
        try:
            if "-1" in self.args['receiver']:
                new_ret['receiver'] = [-1]
            elif self.args['receiver'] == "":
                new_ret['receiver'] = []
                error_args['receiver'] = 'miss'
            else:
                recv_list = [int(i) for i in self.args['receiver'].split(",") if self.db_client.select_one(User, id=int(i))]
                if recv_list:
                    new_ret['receiver'] = recv_list
                else:
                    new_ret['receiver'] = []
                    error_args['receiver'] = 'miss'
        except Exception, ex:
            error_args['receiver'] = 'miss'

        check_fields = [('sender', str), ('title', str), ('content', str), ('type', int)]
        for field, parse in check_fields:
            try:
                new_ret[field] = parse(self.args[field])
                assert new_ret[field]
            except:
                new_ret[field] = self.args[field]
                error_args[field] = "miss"

        return new_ret, error_args

    def send_msg2(self):
        new_args, error_args = self.check_send_msg_args()
        has_error = len(error_args) != 0

        if has_error:
            tips = {}
            for k in error_args:
                tips[k] = view_util.gen_tips()

            recv_list = [{'id':user.id, 'name':user.name} for user in self.db_client.iter_all(User)]
            recv_list.insert(0, {'id':-1, 'name': 'all'})
            ret_dict = {
                'sender':new_args['sender'],
                'mail_title':new_args['title'],
                'content':new_args['content'],
                'mail_type':new_args['type'],
                'scan': False,
                'title': "Create",
                'receiver':[str(i) for i in new_args['receiver']],
                'list_url': global_vars.URL_MSG_LIST,
                'options':{
                    'mail_type':[[k, v] for k, v in MAIL_TYPE.items()],
                    'receiver_list' : recv_list,
                },
                'tips':tips,
                'op_tips':view_util.gen_op_tips("Create Failed!", False)
            }
            tmp_path = "message.tmpl"
            render = Render('Mobitx Create %s'%'Message', self.tmpl_reader, self.session_info)
            body_tmpl = self.tmpl_reader.read_file(tmp_path)
            body_str = Template(body_tmpl).render(**ret_dict)
            return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})
        mail = Mail(**view_util.filter_model_key(Mail, new_args))
        if self.user_db_client.add_one(mail):
            if -1 in new_args['receiver']:
                new_args['receiver'] = [user.id for user in self.db_client.iter_all(User)]
            for uid in new_args['receiver']:
                mail_rec = UserMail(read=0, uid=uid, mid=mail.id)
                self.user_db_client.do_save(mail_rec)
        return redirect(global_vars.URL_MSG_LIST)

    def send_msg1(self):
        recv_list = [{'id':user.id, 'name':user.name} for user in self.db_client.iter_all(User)]
        recv_list.insert(0, {'id':-1, 'name': 'all'})
        ret_dict = {
            'scan': False,
            'title': "Create",
            'list_url': global_vars.URL_MSG_LIST,
            'options':{
                'mail_type':[[k, v] for k, v in MAIL_TYPE.items()],
                'receiver_list' : recv_list,
            },
            'tips':{},
        }
        tmp_path = "message.tmpl"
        render = Render('Mobitx Create %s'%'Message', self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def scan_msg(self):
        msg_id = self.args['id']
        mail_info = self.user_db_client.select_one(UserMail, id=msg_id)
        if mail_info:
            mail = self.user_db_client.select_one(Mail, id=mail_info.mid)
            ltime = time.localtime(mail.create_time)
            timeStr=time.strftime("%Y-%m-%d %H:%M:%S", ltime)
            mail_type = [[k, v] for k, v in MAIL_TYPE.items()]
            recv_list = [{'id':user.id, 'name':user.name} for user in self.db_client.iter_all(User)]
            recv_list.insert(0, {'id':-1, 'name': 'all'})
            ret_dict = {
                'sender':mail.sender,
                'mail_title':mail.title,
                'content':mail.content,
                'mail_type':mail.type,
                'create_time':timeStr,
                'scan': True,
                'title': "Scan",
                'list_url': global_vars.URL_MSG_LIST,
                'options':{
                    'mail_type':[[k, v] for k, v in MAIL_TYPE.items()],
                    'receiver_list' : recv_list,
                },
                'tips':{},
            }
            tmp_path = "message.tmpl"
            render = Render('Mobitx Create %s'%'Message', self.tmpl_reader, self.session_info)
            body_tmpl = self.tmpl_reader.read_file(tmp_path)
            body_str = Template(body_tmpl).render(**ret_dict)
            if mail_info.read == 0 and mail_info.uid == self.my_uid:
                mail_info.read = 1
                self.user_db_client.do_save(mail_info)
            return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})
        else:
            return self.msg_list()
