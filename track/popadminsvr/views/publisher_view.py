from flask import redirect, request

from db_client import WebSite
from view_util import Render, to_links, get_request_args
import global_vars


class WebsiteView():
    def __init__(self, session_info):
        self.table_class = WebSite
        self.session_info = session_info
        self.name2table = {}
        #for _table in global_vars.all_tables:
        #    self.name2table[_table.__tablename__] = _table

        self.db_client = global_vars.global_db_set.get_db_client()
        self.my_uid = view_util.username2uid(session_info['username'], self.db_client)
        self.args = get_request_args()
        self.args['uid'] = self.my_uid
        self.tmpl_reader = global_vars.tmpl_reader
        self.list_url = get_model_uri(self.table_class, 'list')

    def load_tmp(self, ret_dict, tmp_path):
        render = Render('Mobitx Create %s'%self.table_class.__name__, self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file(tmp_path)
        body_str = Template(body_tmpl).render(**ret_dict)
        return render.gen_output(body_str, {'nav_left' : to_links(self.table_class, 'list')})

    def test(self):
        return self.load_tmp({}, "website.tmpl")

