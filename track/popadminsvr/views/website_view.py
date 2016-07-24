from flask import redirect, request
import urllib

from db_client import Website, WebsiteBid, get_columns, get_foreign_source_keys, get_foreign_keys
from view_utils import Render, to_links, username2uid
from mako.template import Template
import utils
import view_utils
import global_vars
import ujson
from config import country_config, os_config, browser_config


class WebsiteView():
    def __init__(self, session_info):
        self.session_info = session_info
        self.name2table = {}
        for _table in global_vars.all_tables:
            self.name2table[_table.__tablename__] = _table

        self.db_client = global_vars.global_db_set.get_db_client()
        self.my_uid = username2uid(session_info['username'], session_info['type'], self.db_client)
        self.args = utils.get_request_args()
        self.args['uid'] = self.my_uid
        self.tmpl_reader = global_vars.tmpl_reader

    def load_tmp(self, ret_dict, tmp_path, table_class):
        render = Render('Mobitx Create %s'%table_class.__name__ if table_class else "", self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return body_str

    def test(self):
        render = Render('Mobitx Create', self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file("default.tmpl")
        body_str = Template(body_tmpl).render()
        return body_str

    def output_add(self, save=False):
        ret = {'title':"Add New Website", 'tips':{}, "list_url":global_vars.URL_WEBSITE_LIST, "nav_title":"Create"}
        if not save:
            return self.load_tmp(ret, "website.tmpl", Website)
        else:
            new_args, error_args = view_utils.check_create_args(self.args, Website, self.name2table, self.db_client)
            has_error = len(error_args) != 0
            if has_error:
                ret.update(new_args)
                for k, v in error_args.items():
                    ret['tips'][k] = "field is unique!" if v == "unique" else "field is error!"
                ret['optips'] = view_utils.gen_op_tips("Create Failed!")
                return self.load_tmp(ret, "website.tmpl", Website)
            else:
                model = Website(**new_args)
                if self.db_client.add_one(model):
                    return redirect("%s?id=%d&create=1"%(global_vars.URL_WEBSITE_EDIT,model.id))
                else:
                    ret['optips'] = view_utils.gen_op_tips("Create Failed!")
                    return self.load_tmp(ret, "website.tmpl", Website)


    def output_list(self):
        sites = self.db_client.select_all(Website, uid=self.my_uid)
        normal_columns = get_columns(Website)
        ret = []
        filter_fields = ["uid"]
        for site in sites:
            site_dict = {}
            for col in normal_columns:
                if col.name in filter_fields:
                    continue
                site_dict[col.name] = getattr(site, col.name)
            ret.append(site_dict)
        ret_dict = {
            "site_list": ujson.dumps(ret),
            "edit_url": global_vars.URL_WEBSITE_EDIT,
            "add_url":global_vars.URL_WEBSITE_ADD,
        }

        return self.load_tmp(ret_dict, "website_list.tmpl", Website)

    def output_edit(self, save=False):
        ret = {'title':"Edit Your Website", 'tips':{}, "list_url":global_vars.URL_WEBSITE_LIST, "nav_title":"Edit"}
        if save:
            new_args, error_args = view_utils.check_create_args(self.args, Website, self.name2table, self.db_client, check_primary=True)
            has_error = len(error_args) != 0
            ret.update(new_args)
            if has_error:
                for k, v in error_args.items():
                    ret['tips'][k] = "field is unique!" if v == "unique" else "field is error!"
                ret['optips'] = view_utils.gen_op_tips("Edit Failed!")
                return self.load_tmp(ret, "website.tmpl", Website)
            else:
                model = Website(**new_args)
                if self.db_client.do_save(model):
                    ret['optips'] = view_utils.gen_op_tips("Edit Success!", True)
                    return self.load_tmp(ret, "website.tmpl", Website)
                else:
                    ret['optips'] = view_utils.gen_op_tips("Edit Failed!")
                    return self.load_tmp(ret, "website.tmpl", Website)


        else:
            site_id = int(self.args['id'])
            url = global_vars.URL_WEBSITE_EDIT
            params = {'id':site_id}
            if self.args.get('create'):
                ret['optips'] = view_utils.gen_op_tips("Create Success!", True)
                params['create'] = 1

            model = self.db_client.select_one(Website, id=site_id)
            filter_fields = ["uid"]
            site_dict = {}
            for col in get_columns(Website):
                if col.name in filter_fields:
                    continue
                site_dict[col.name] = getattr(model, col.name)
            ret.update(site_dict)
            params = urllib.urlencode(params)
            url = "%s?%s"%(url, params)
            return {"url":url, "html": self.load_tmp(ret, "website.tmpl", Website)}

    def bid_list(self):
        sites = self.db_client.select_all_left_join_filter_by_right_col(WebsiteBid, Website, WebsiteBid.wid, Website.id, Website.uid, self.my_uid)
        normal_columns = get_columns(WebsiteBid)
        foreign_columns = get_foreign_keys(WebsiteBid)
        ret = []
        filter_fields = ["uid"]
        for site in sites:
            site_dict = {}
            for col in normal_columns:
                if col.name in filter_fields:
                    continue
                site_dict[col.name] = getattr(site, col.name)
            ret.append(site_dict)
        ret_dict = {
            "data_list": ujson.dumps(ret),
            "edit_url": global_vars.URL_WEBSITE_BID_EDIT,
            "add_url": global_vars.URL_WEBSITE_BID_ADD,
        }

        return self.load_tmp(ret_dict, "website_bid_list.tmpl", WebsiteBid)


    def bid_add(self, save=False):
        ret = {
            'title':"Add New Website Bid",
            'tips':{},
            "nav_title":"Create",
            "list_url":global_vars.URL_WEBSITE_BID_LIST,
            'options': {
                'country': country_config.COUNTRY_NAME_LIST,
                'os': os_config.OS_LIST,
                'browser': browser_config.BROWSER_LIST,
                'wid': view_utils.get_foreign_key_options(self.db_client, Website, 'name'),
            },
        }
        if not save:
            return self.load_tmp(ret, "website_bid.tmpl", WebsiteBid)
        else:
            new_args, error_args = view_utils.check_create_args(self.args, WebsiteBid, self.name2table, self.db_client)
            has_error = len(error_args) != 0
            if has_error:
                ret.update(new_args)
                for k, v in error_args.items():
                    ret['tips'][k] = "field is unique!" if v == "unique" else "field is error!"
                ret['optips'] = view_utils.gen_op_tips("Create Failed!")
                return self.load_tmp(ret, "website_bid.tmpl", WebsiteBid)
            else:
                model = WebsiteBid(**new_args)
                if self.db_client.add_one(model):
                    return redirect("%s?id=%d&create=1"%(global_vars.URL_WEBSITE_BID_EDIT,model.id))
                else:
                    ret['optips'] = view_utils.gen_op_tips("Create Failed!")
                    return self.load_tmp(ret, "website_bid.tmpl", WebsiteBid)


    def bid_edit(self, save=False):
        ret = {
            'title':"Edit Your Website Bid",
            'tips':{},
            "nav_title":"Edit",
            "list_url":global_vars.URL_WEBSITE_BID_LIST,
            'options': {
                'country': country_config.COUNTRY_NAME_LIST,
                'os': os_config.OS_LIST,
                'browser': browser_config.BROWSER_LIST,
                'wid': view_utils.get_foreign_key_options(self.db_client, Website, 'name'),
            },
        }
        if not save:
            camp_id = int(self.args['id'])
            url = global_vars.URL_WEBSITE_BID_EDIT
            params = {"id":camp_id}
            if self.args.get('create'):
                params['create'] = 1
                ret['optips'] = view_utils.gen_op_tips("Create Success!", True)

            model = self.db_client.select_one(WebsiteBid, id=camp_id)
            filter_fields = ["uid"]
            site_dict = {}
            for col in get_columns(WebsiteBid):
                if col.name in filter_fields:
                    continue
                site_dict[col.name] = getattr(model, col.name)
            ret.update(site_dict)
            params = urllib.urlencode(params)
            url = "%s?%s"%(url, params) if params else url
            return {"url":url, "html": self.load_tmp(ret, "website_bid.tmpl", WebsiteBid)}

        else:
            new_args, error_args = view_utils.check_create_args(self.args, WebsiteBid, self.name2table, self.db_client, check_primary=True)
            has_error = len(error_args) != 0
            ret.update(new_args)
            if has_error:
                for k, v in error_args.items():
                    ret['tips'][k] = "field is unique!" if v == "unique" else "field is error!"
                ret['optips'] = view_utils.gen_op_tips("Edit Failed!")
                return self.load_tmp(ret, "website_bid.tmpl", WebsiteBid)
            else:
                model = WebsiteBid(**new_args)
                if self.db_client.do_save(model):
                    ret['optips'] = view_utils.gen_op_tips("Edit Success!", True)
                    return self.load_tmp(ret, "website_bid.tmpl", WebsiteBid)
                else:
                    ret['optips'] = view_utils.gen_op_tips("Edit Failed!")
                    return self.load_tmp(ret, "website_bid.tmpl", WebsiteBid)

