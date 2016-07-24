#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from os import path as osp
from mako.template import Template


def to_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        return s.decode('utf8')


def read_content(file_name):
    with open(file_name, 'r') as f:
        return f.read()



class TemplateItem(object):
    def __init__(self, path):
        self.last_mt = osp.getmtime(path)
        self.real_tmpl = Template(to_unicode(read_content(path)))
        self.path = path



class TemplatePool(object):
    def __init__(self):
        self.cached_templates = {}

    def get_template_by_path(self, path):
        last_mtime = osp.getmtime(path)
        tmpl_obj = self.cached_templates.get(path)
        if tmpl_obj is None or last_mtime != tmpl_obj.last_mt:
            tmpl_obj = TemplateItem(path)
            self.cached_templates[path] = tmpl_obj

        return tmpl_obj.real_tmpl

    def clear(self):
        self.cached_templates = {}




class TemplateCacheItem(object):
    def __init__(self, tmpl_id, tmpl_str):
        self.tmpl_id = tmpl_id
        self.last_access_time = int(time.time())
        self.tmpl_str = tmpl_str
        self.real_tmpl = Template(to_unicode(tmpl_str))


class TemplateCache(object):
    def __init__(self, size=-1):
        self.cached_templates = {}
        self.size = size

    def get_template_by_id(self, tmpl_id, cur_tmpl_str):
        tmpl_obj = self.cached_templates.get(tmpl_id)
        if tmpl_obj and tmpl_obj.tmpl_str == cur_tmpl_str:
            tmpl_obj.last_access_time = int(time.time())
        else:
            tmpl_obj = TemplateCacheItem(tmpl_id, cur_tmpl_str)
            self.cached_templates[tmpl_id] = tmpl_obj

        return tmpl_obj.real_tmpl

    def clear(self):
        self.cached_templates = {}


def test_cache():
    cache = TemplateCache()
    d = {'name' : 'Season'}

    id1 = '101'
    id2 = '102'
    tmpl_str1 = 'Hello World ${name}'
    tmpl_str2 = 'Foo Bar ${name}'

    tmpl1 = cache.get_template_by_id(id1, tmpl_str1)
    assert len(cache.cached_templates) == 1

    tmpl2 = cache.get_template_by_id(id2, tmpl_str2)
    tmpl3 = cache.get_template_by_id(id1, tmpl_str1)
    tmpl4 = cache.get_template_by_id(id1, tmpl_str1)
    tmpl5 = cache.get_template_by_id(id1, tmpl_str1)
    tmpl6 = cache.get_template_by_id(id1, tmpl_str1)

    assert tmpl1 == tmpl3
    assert len(cache.cached_templates) == 2
    assert tmpl1.render(**d) == tmpl3.render(**d)

    assert tmpl1.render(**d) == 'Hello World Season'
    assert tmpl2.render(**d) == 'Foo Bar Season'


if __name__ == '__main__':
    test_cache()


