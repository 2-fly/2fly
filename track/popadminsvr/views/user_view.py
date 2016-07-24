from view_utils import Render, to_links, username2uid
from db_client import Advertiser, Publisher
from mako.template import Template
from flask import make_response, render_template, redirect
import utils
import global_vars
import view_utils
import time

class UserView():
    def __init__(self, session_info):
        self.session_info = session_info
        self.name2table = {}

        self.db_client = global_vars.global_db_set.get_db_client()
        self.my_uid = username2uid(session_info['username'], session_info['type'], self.db_client)
        self.args = utils.get_request_args()
        self.args['uid'] = self.my_uid
        self.tmpl_reader = global_vars.tmpl_reader

    def get_account_tmpl(self, ret):
        render = Render('Mobitx Create %s', self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file('user_info.tmpl')
        body_str = Template(body_tmpl).render(**ret)
        return body_str

    def edit_account_tmpl(self, ret):
        render = Render('Mobitx Create %s', self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file('user_info.tmpl')
        body_str = Template(body_tmpl).render(**ret)
        return body_str

    def get_account(self):
        username = self.session_info['username']
        t = int(self.session_info['type'])
        suc = self.args.get("success")

        cls = Publisher if t == global_vars.PUBLISHER else Advertiser
        user = self.db_client.select_one(cls, name=username)

        ret = {'tips':{}, 'email':user.email}
        if suc:
            ret['optips'] = view_utils.gen_op_tips("Edit Success!", True)
        return self.get_account_tmpl(ret)


    def modify_account(self):
        old_pwd = self.args.get("origin_password")
        pwd = self.args.get("password")
        email = self.args.get("email")
        error = {}

        username = self.session_info['username']
        t = int(self.session_info['type'])
        cls = Publisher if t == global_vars.PUBLISHER else Advertiser
        user = self.db_client.select_one(cls, name=username)
        ret = {'tips':{}, 'email':user.email}

        if not pwd or len(pwd) < 6:
            error['password'] = "field error"
        if not email:
            error['email'] = "field error"
        if utils.gen_secret(old_pwd) != user.password:
            error['origin_password'] = "field error!"
        if not error:

            pwd = utils.gen_secret(pwd)
            user.password = pwd
            user.email = email
            self.db_client.do_save(user)
            ret['optips'] = view_utils.gen_op_tips("Edit Success!", True)
            ret = self.edit_account_tmpl(ret)
            resp = make_response(redirect("%s?success=1"%global_vars.URL_MODIFY_USER))
            self.set_user_session(resp, username, pwd, int(time.time()), t)
            return resp
        else:
            for k, v in error.items():
                ret['tips'][k] = v
            ret['optips'] = view_utils.gen_op_tips("Edit Failed!")
            return self.edit_account_tmpl(ret)

    def set_user_session(self, resp, username, password, ts, t):
        skey = utils.gen_skey(username, password, ts)
        resp.set_cookie('username', username)
        resp.set_cookie('skey', skey)
        resp.set_cookie('time', str(ts))
        resp.set_cookie("type", str(t))


