from flask import redirect, request
import urllib

from db_client import Campaign, get_columns
from view_utils import Render, to_links, username2uid
from mako.template import Template
from config import country_config, os_config, browser_config, ads_config
from os import path as osp, listdir
import os
import utils
import view_utils
import global_vars
import ujson
import settings

SIZE_CONFIG = (
    "320*50", "300*250", "320*480", "216*36", "120*20", "160*600", "300*50", "480*80", "480*320", "480*800", "640*960", "728*90",
    "768*1024", "960*640", "1024*768", "240*38", "480*75", "582*166", "600*500", "640*100", "640*1136", "480*44", "480*60",
    "300*300", "600*600", "1200*1200", "240*38", "960*150", "360*300"
)

class CampaignView():
    def __init__(self, session_info):
        self.table_class = Campaign
        self.session_info = session_info
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table

        self.db_client = global_vars.global_db_set.get_db_client()
        self.my_uid = username2uid(session_info['username'], session_info['type'], self.db_client)
        self.args = utils.get_request_args()
        self.args['uid'] = self.my_uid
        self.tmpl_reader = global_vars.tmpl_reader
        self.list_url = utils.get_model_uri(self.table_class, 'list')

    def load_tmp(self, ret_dict, tmp_path):
        if "adm" in ret_dict:
            ret_dict["adm"] = utils.decode_from_utf8(ret_dict["adm"])
        render = Render('Mobitx Create %s'%Campaign.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return body_str

    def change_website_list(self, cpid, op_type, website_list):
        website_list = set(website_list)
        obj = self.db_client.select_one(Campaign, id=cpid, uid=self.my_uid)
        if not obj:
            return False
        include = set(obj.include_websites.split(",")) if obj.include_websites else set()
        exclude = set(obj.exclude_websites.split(",")) if obj.exclude_websites else set()
        if op_type == "rm-include":
            include = include - website_list
        elif op_type == "add-include":
            include = include | website_list
        elif op_type == "add-exclude":
            exclude = exclude | website_list
        else:
            return False
        include = ",".join([e for e in include if e])
        exclude = ",".join([e for e in exclude if e])
        obj.include_websites = include
        obj.exclude_websites = exclude
        return self.db_client.do_save(obj)


    def init_option(self):
        return {
            'country': country_config.COUNTRY_NAME_LIST,
            'os': os_config.OS_LIST,
            'browser': browser_config.BROWSER_LIST,
            'image_size': SIZE_CONFIG,
            'category' : ads_config.ADS_LIST_CONFIG
        }

    def edit(self, save=False):
        ret = view_utils.init_tmpl_dict()
        ret.update({
            'title':"Edit Your Campaign",
            'tips':{},
            'nav_title':"Edit",
            "clone_url":global_vars.URL_CAMP_ADD,
            'cur_url':global_vars.URL_CAMP_EDIT,
            'list_url':global_vars.URL_CAMP_LIST,
            'options': self.init_option(),
            'upload_js_ac_url' : global_vars.URL_UPLOAD_JS_AC,
        })
        if not save:
            camp_id = int(self.args['id'])
            url = ""
            if self.args.get('create'):
                ret['optips'] = view_utils.gen_op_tips("Create Success!", True)
                url = global_vars.URL_CAMP_EDIT
                params = urllib.urlencode({"id":camp_id, "create":1})
                url = "%s?%s"%(url, params)

            model = self.db_client.select_one(Campaign, id=camp_id, uid=self.my_uid)
            filter_fields = ["uid"]
            site_dict = {}
            for col in get_columns(Campaign):
                if col.name in filter_fields:
                    continue
                site_dict[col.name] = getattr(model, col.name)
            site_dict["adm"] = self.get_adm_html_style(site_dict["adm"])
            ret.update(site_dict)
            body_str = self.load_tmp(ret, "campaign.tmpl")
            return body_str if not url else {"url":url, "html":body_str}

        else:
            if "adm" in self.args:
                self.args["adm"] = self.get_adm(self.args["adm"])
            new_args, error_args = self.check_create_args(True)
            has_error = len(error_args) != 0
            ret.update(new_args)
            if has_error:
                for k, v in error_args.items():
                    if type(v) == dict:
                        ret['tips'][k] = v['msg']
                    else:
                        ret['tips'][k] = "field is unique!" if v == "unique" else "field is error!"
                ret['optips'] = view_utils.gen_op_tips("Edit Failed!")
                return self.load_tmp(ret, "campaign.tmpl")
            else:
                model = Campaign(**new_args)
                if self.db_client.do_save(model):
                    ret.update(new_args)
                    ret['optips'] = view_utils.gen_op_tips("Edit Success!", True)
                    self.log_camp(model)
                    return self.load_tmp(ret, "campaign.tmpl")
                else:
                    ret['optips'] = view_utils.gen_op_tips("Edit Failed!")
                    return self.load_tmp(ret, "campaign.tmpl")

    def log_camp(self, camp):
        ret = []
        for col in get_columns(Campaign):
            ret.append("%s : %s"%(col.name, getattr(camp, col.name)))
        print " | ".join(ret)

    def add(self, save=False):
        ret = view_utils.init_tmpl_dict()
        ret.update({
            'title':"Add New Campaign",
            'tips':{},
            "cur_url":global_vars.URL_CAMP_ADD,
            'nav_title':"Create",
            'list_url':global_vars.URL_CAMP_LIST,
            'options': self.init_option(),
            'upload_js_ac_url' : global_vars.URL_UPLOAD_JS_AC,
        })
        clone = self.args.get("clone", 0)

        if clone:
            new_args, _ = self.check_create_args()
            ret.update(new_args)
            if 'name' not in ret:
                return redirect(global_vars.URL_CAMP_ADD)
            if 'id' in ret:
                ret.pop('id')
            ret['name'] = "(New)" + ret['name']
            ret['optips'] = view_utils.gen_op_tips("Clone Success!", True)
            return self.load_tmp(ret, "campaign.tmpl")
        elif not save:
            return self.load_tmp(ret, "campaign.tmpl")
        else:
            if "adm" in self.args:
                self.args["adm"] = self.get_adm(self.args["adm"])
            new_args, error_args = self.check_create_args()
            has_error = len(error_args) != 0
            if has_error:
                ret.update(new_args)
                for k, v in error_args.items():
                    if type(v) == dict:
                        ret['tips'][k] = v['msg']
                    else:
                        ret['tips'][k] = "field is unique!" if v == "unique" else "field is error!"
                ret['optips'] = view_utils.gen_op_tips("Create Failed!")
                return self.load_tmp(ret, "campaign.tmpl")
            else:
                model = Campaign(**new_args)
                self.log_camp(model)
                if self.db_client.add_one(model):
                    return redirect("%s?id=%d&create=1"%(global_vars.URL_CAMP_EDIT,model.id))
                else:
                    ret['optips'] = view_utils.gen_op_tips("Create Failed!")
                    return self.load_tmp(ret, "campaign.tmpl")

    def check_create_args(self, check_primary=False):
        new_args, error_args = view_utils.check_create_args(self.args, Campaign, self.name2table, self.db_client, check_primary=check_primary)
        #if len(new_args['image_url'].split(",")) != len(new_args['image_width_height'].split(",")):
        #    msg = "length doesn't match"
        #    error_args['image_url'] = {'msg':msg}
        #    error_args['image_width_height'] = {'msg':msg}
        return new_args, error_args

    def list(self):
        datas = self.db_client.select_all(Campaign, uid=self.my_uid)
        normal_columns = get_columns(Campaign)
        ret = []
        filter_fields = ["uid", "include_websites", "exclude_websites"]
        v2k_fields = ['os', 'browser', 'country']

        conf = {}
        conf['os'] = self.get_value_key_map(os_config.OS_LIST)
        conf['browser'] = self.get_value_key_map(browser_config.BROWSER_LIST)
        conf['country'] = self.get_value_key_map(country_config.COUNTRY_NAME_LIST)

        for data in datas:
            site_dict = {}
            for col in normal_columns:
                if col.name in filter_fields:
                    continue
                if col.name in v2k_fields:
                    site_dict[col.name] = ",".join([conf[col.name][d] for d in getattr(data, col.name).split(",") if d in conf[col.name]])
                if col.name == "status":
                    site_dict[col.name] = "On" if getattr(data, col.name) else "Off"
                else:
                    site_dict[col.name] = getattr(data, col.name)
            ret.append(site_dict)


        ret_dict = {
            "data_list": ujson.dumps(ret),
            "edit_url": global_vars.URL_CAMP_EDIT,
            "add_url":global_vars.URL_CAMP_ADD,
        }

        return self.load_tmp(ret_dict, "campaign_list.tmpl")

    def get_value_key_map(self, conf):
        d = {}
        for i in conf:
            d[i[1]] = i[0]
        return d

    def get_adm(self, adm):
        adm = adm.encode("utf8")
        return adm

    def get_adm_html_style(self, adm):
        adm = adm or ""
        adm = adm.replace('"', "&quot;")
        adm = adm.replace('<', "&lt;")
        adm = adm.replace('<', "&gt;")
        return adm

    def _get_ac_js_name(self, url):
        parts = url.split("?")
        if len(parts) > 1:
            url = parts[0]
        js_name = url[url.rindex("/")+1:]
        return "%s.js" % js_name

    def upload_js_ac(self):
        js_camp_url = self.args["js_camp_url"]
        image_urls = self.args["image_urls"]
        exchange = int(self.args["exchange_type"])
        domain = self.args["domain"]
        result = {
            "err" : True,
        }
        if exchange == 0:
            return ujson.dumps(result)

        CRAZY_EXCHANGE_LIST = [2]
        py_file = "convert_freq2.py" if exchange not in CRAZY_EXCHANGE_LIST  else "convert_crazy.py"
        tmp_js_name = "pop_freq2.js.output" if exchange not in CRAZY_EXCHANGE_LIST else "pop_crazy.js.output"

        cur_dir = os.getcwd()
        path = osp.join(cur_dir, "tools/ac_tools")
        js_name = self._get_ac_js_name(js_camp_url)
        err = False
        try:
            cmd = "cd %s;python %s \"%s\" \"%s\";mv %s/%s %s/output/%s" % (path, py_file, js_camp_url, image_urls, path, tmp_js_name, path, js_name)
            os.system(cmd)
            upload_cmd = "rsync -avz %s/output/%s v3_ftp:/home/ec2-user/assets/55/jjs/" % (path, js_name)
            os.system(upload_cmd)
        except:
            err = True
        result["err"] = err
        result["jc_js_url"] = "http://%s/assets/55/jjs/%s" % (domain, js_name)
        return ujson.dumps(result)

    def change_camp_status(self, cid, status):
        model = self.db_client.select_one(Campaign, id=cid, uid=self.my_uid)
        model.status = status
        return self.db_client.do_save(model)

