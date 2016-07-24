from flask import redirect, request, jsonify
from datetime import datetime
import urllib
import hashlib
import mimetypes
import os, sys
import os.path
import re
import shutil
import time


from view_utils import Render, to_links, username2uid
from mako.template import Template
from elFinder import connector
import utils
import view_utils
import global_vars
import ujson
import settings

class ImgMgrView():
    def __init__(self, session_info):
        self.session_info = session_info
        self.my_uid = username2uid(session_info['username'], session_info['type'], global_vars.global_db_set.get_db_client())
        self.args = utils.get_request_args()
        self.args['uid'] = self.my_uid
        self.tmpl_reader = global_vars.tmpl_reader

    def output_view(self):
        ret = {"op_url": global_vars.URL_IMG_OP}
        return self.load_tmp(ret)

    def handler_file_op(self):
        img_dir = os.path.join(settings.img_dir, str(self.my_uid))
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)

        opts = {
            'root': img_dir,
            'URL': '.',
            'uploadAllow' : ["image"],
            'uploadOrder' : ['allow']
        }

        elf = connector(opts)

        # fetch only needed GET/POST parameters
        httpRequest = {}
        for field in elf.httpAllowedParameters:
            if field in self.args:
                httpRequest[field] = self.args.get(field)

                if field == 'upload[]':
                    upFiles = {}
                    upload_files = self.args[field]
                    if not isinstance(upload_files, list):
                        upload_files = [upload_files]
                    for up in upload_files:
                        if up.filename:
                            upFiles[up.filename] = up.stream # pack dict(filename: filedescriptor)
                    httpRequest[field] = upFiles

        # run connector with parameters
        status, header, response = elf.run(httpRequest)

        # code below is tested with apache only (maybe other server need other method?)
        res = ""
        if not response is None and status == 200:
            if 'file' in response and isinstance(response['file'], file):
                res =  response['file'].read()
                response['file'].close()
                return res
            else:
                res = ujson.dumps(response)
                res = jsonify(response)
        return res


    def load_tmp(self, ret_dict):
        render = Render('Mobitx Image Manager', self.tmpl_reader, self.session_info)
        body_tmpl = self.tmpl_reader.read_file('img_mgr.tmpl')
        body_str = Template(body_tmpl).render(**ret_dict)
        return body_str


