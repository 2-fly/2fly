#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import hashlib

import init_env
import adminsvr.settings as settings

from adminsvr.db_client import *
from adminsvr.global_vars import global_db_set as DBSet, tmpl_reader



def gen_secret(passwd):
    return hashlib.md5(passwd + '_' + settings.app_secret).hexdigest()


def create_account(username, password, email, permission):
    hash_password = gen_secret(password)
    user = User(name=username, password=hash_password, email=email, permission=permission)
    DBSet.get_db_client().do_save(user)
    return True


def modify_account(username, password):
    hash_password = gen_secret(password)
    user_info = dict(password=hash_password)
    DBSet.get_db_client().do_update(User, {'name' : username}, user_info)
    return True

def permission_accout(username, permission):
    user_info = dict(permission=permission)
    DBSet.get_db_client().do_update(User, {'name' : username}, user_info)
    return True

def print_usage(prog_name):
    print 'usage %s: create username password email permission'%prog_name
    print 'usage %s: modify username password'%prog_name
    print 'usage %s: permission username permission'%prog_name



if __name__ == '__main__':
    if len(sys.argv) < 4:
        print_usage(sys.argv[0])
        exit(-1)
    DBSet.set_init(True)
    if sys.argv[1] == 'create':
        if len(sys.argv) < 5:
            print_usage(sys.argv[0])
            exit(-1)
        if len(sys.argv) < 6:
            permission = 6
        else:
            permission = int(sys.argv[5])
        create_account(sys.argv[2], sys.argv[3], sys.argv[4], permission)
    elif sys.argv[1] == 'modify':
        modify_account(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'permission':
        permission_accout(sys.argv[2], sys.argv[3])
    else:
        print_usage(sys.argv[0])

