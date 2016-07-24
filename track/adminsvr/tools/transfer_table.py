#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
from os import path as osp
import init_env
from adminsvr.db_client import *
from adminsvr.global_vars import global_db_set as DBSet

def transfer_landpage(from_uid, to_uid):
    landers = DBSet.get_db_client().iter_all(LandingPage, uid=from_uid)
    count = 0
    for o in landers:
        args = {
            "name" : o.name,
            "source" : o.source,
            "uid" : to_uid,
            "hidden" : o.hidden,
            "lander_mode" : o.lander_mode,
            "lander_link" : o.lander_link,
        }
        model = LandingPage(**args)
        if not DBSet.get_db_client().do_save(model):
            print "save uid(%s) landpage(%s) to uid(%s) failed." % (from_uid, o.id, to_uid)
        else:
            count = count + 1
    print "transfer landpange %s, total(%s)" % (count, len(landers))

def transfer_table(from_uid, to_uid):
    DBSet.set_init(True)
    transfer_landpage(from_uid, to_uid)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "python transfer_table.py from_uid to_uid."
        exit(-1)
    from_uid = int(sys.argv[1])
    to_uid = int(sys.argv[2])
    transfer_table(from_uid, to_uid)
