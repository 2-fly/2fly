#!/usr/bin/env python
# -*-coding:utf-8 -*-
from mako.template import Template
import global_vars
from view import Render, to_links

def handle_help_view(session_info):
    ret_dict = {}
    tmp_path = "help.tmpl"
    render = Render('Mobitx help', global_vars.tmpl_reader, session_info)
    body_tmpl = global_vars.tmpl_reader.read_file(tmp_path)
    body_str = Template(body_tmpl).render(**ret_dict)
    return render.gen_output(body_str, {'nav_left' : to_links('help')})
