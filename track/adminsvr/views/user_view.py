 #!/usr/bin/env python
# -*-coding:utf-8 -*-
from view import ModelView, Render
from utils import get_model_uri, to_links
from mako.template import Template
from db_client import User, Campaign
from config.rule_config import rule, rule_type
from tools import account_tools
from commlib.db.redis_helper import RedisHashTable2
from commlib.db.db_tabledef import virus_domains_key, virusdomains_admin_table, verify_domains_key
from commlib.utils.httputils import is_subdomain

import settings
import ujson
import global_vars
import view_util
import verify_urls

def gen_op_tips(tips, success=False):
    if not success:
        return '''<div class="alert alert-error"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></div>'''%tips
    else:
        return '''<div class="alert alert-success"><button type="button" class="close" data-dismiss="alert">&times;</button><strong>%s</strong></div>'''%tips

def gen_tips():
    return '<span class="label label-important" style="margin-left:20px">field is error!</span>'

class UserView(ModelView):
    def __init__(self, session_info):
        self.table_class = User
        self.tmpl_reader = global_vars.tmpl_reader
        self.session_info = session_info
        self.db_client = global_vars.global_db_set.get_db_client()
        self.redis_cli = global_vars.global_db_set.get_redis_db()
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.args = view_util.get_request_args()
        self.args['uid'] = self.my_uid

    def output_edit(self, save=False):
        ret_dict = {'ret':"", "submit_url":global_vars.URL_BASIC_INFO_EDIT}
        if save:
            user = User(
                    id=self.my_uid,
                    lander_domains=self.args['lander_domains'],
                    timezone=self.args['time_zone'],
                    track_domains=self.args['track_domains'],
            )
            if self.db_client.do_save(user):
                ret_dict['ret'] = gen_op_tips("Edit Success!", True)
            else:
                ret_dict['ret'] = gen_op_tips("Edit Failed!", False)
        else:
            user = self.db_client.select_one(User, id=self.my_uid)

        camp_rows = self.db_client.iter_all(Campaign, uid=self.my_uid)

        lander_domains = [i if len(i.split(";")) > 1 else i + ";0" for i in user.lander_domains.split(",")] if user.lander_domains else []
        track_domains = [i if len(i.split(";")) > 1 else i + ";0" for i in user.track_domains.split(",")] if user.track_domains else []

        track_camp, lander_camp = self.get_domain_num(camp_rows)
        lander_domains = ",".join(lander_domains)
        track_domains = ",".join(track_domains)

        tmp_path = "basic_info.tmpl"
        ret_dict['timezone'] = user.timezone
        ret_dict['lander_domains'] = lander_domains
        ret_dict['track_domains'] = track_domains
        ret_dict['verify_url'] = global_vars.URL_BASIC_INFO_VERIFY_URL
        ret_dict['virus_url'] = global_vars.URL_BASIC_INFO_VIRUS_URL
        ret_dict['query_lander_domain_url'] = global_vars.URL_CAMP_LIST
        ret_dict['lander_camp'] = ujson.dumps(lander_camp)
        ret_dict['track_camp'] = ujson.dumps(track_camp)

        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'edit')})


    def get_domain_num(self, camp_list):
        track_domain = {}
        lander_domain = {}
        for camp in camp_list:
            self.count_domain(camp.lander_domains_dist, lander_domain)
            self.count_domain(camp.track_domain, track_domain)
        return track_domain, lander_domain

    def count_domain(self, domains, ret):
        domains = [s.split(";")[0] for s in domains.split(",") if s.strip()]
        for d in domains:
            count = ret.get(d, 0)
            ret[d] = count + 1

    def verify_domains(self, username):
        urls = [i.split(";")[0] for i in self.args['urls'].split(",")]
        ret = {}
        tmp = []
        for url in urls:
            r = self.redis_cli.get_one(verify_domains_key, url)
            if not r:
                tmp.append(url)
                continue
            ret[url] = ujson.loads(r)

        if tmp:
            verify_res =  verify_urls.verify_all(tmp, username)
            ret.update(verify_res)
            for domain, res in verify_res.items():
                self.redis_cli.add_one(verify_domains_key, domain, ujson.dumps(res))
        for _, v in ret.iteritems():
            v['ret'] = 'Success' if v['ret'] >= 0 else "Fail"
        return ujson.dumps(ret)

    def virus_domains(self):
        ret = {}
        #params={'domains':self.args['urls']}
        #resp = requests.get(settings.global_query_url, params=params)
        for url in self.args['urls'].split(","):
            url_ret = self.redis_cli.get_one(virusdomains_admin_table, url)
            if not url_ret:
                ret[url] = {'ret':""}
            else:
                url_ret = ujson.loads(url_ret)
                detail = '(%d/%d)'%(url_ret['positives'], url_ret['total'])
                status = 'bad' if url_ret['positives'] > 0 else 'good'
                ret[url] = {'ret':"&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp".join([status + detail, url_ret['scan_date']])}
        return ujson.dumps(ret)

    def output_change_pwd(self, save=False):
        ret_dict = {'submit_url': global_vars.URL_CHANGE_PWD,'ret':"", "old_error":""}
        if save:
            self.save_password(ret_dict)
        tmp_path = "change_pwd.tmpl"
        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'change_pwd')})

    def save_password(self, ret_dict):
        try:
            assert self.args.get('new') and self.args['new'] == self.args['comfirn']
            user = self.db_client.select_one(User, id=self.my_uid)
            self.args['old'] = account_tools.gen_secret(self.args['old'])
            self.args['new'] = account_tools.gen_secret(self.args['new'])
            if self.args['old'] != user.password:
                ret_dict["old_error"] = gen_tips()
                assert None
            user.password = self.args['new']
            assert self.db_client.do_save(user)
            ret_dict['ret'] = gen_op_tips("Edit Success!", True);
        except Exception:
            ret_dict['ret'] = gen_op_tips("Edit Failed!")


