#!/usr/bin/env python
# -*- coding:utf-8 -*-

from permission_config import *

NO_AFFILIATE = "Custom"
#MOBVISTA_AFFILIATE = "Mobvista"
MOBVISTA_AFFILIATE = "Direct Massival"
YOUMI_AFFILIATE = "youmi"
APPFLOOD_AFFILIATE = "AppFlood"
NOT_DIRECT_MASSIVAL = "Normal Massival"

AF_TYPE_NORMAL = 0
AF_TYPE_DIRECT = 1

AFFILIATE_LIST = [
    (0, NO_AFFILIATE, "show", AF_TYPE_NORMAL, PERMISSION_CONFIGURE_CUSTOM_OFFER),
    (1, MOBVISTA_AFFILIATE, "show", AF_TYPE_DIRECT, PERMISSION_CONFIGURE_DIRECT_OFFER),
    (2, YOUMI_AFFILIATE, "hide", AF_TYPE_DIRECT, PERMISSION_CONFIGURE_DIRECT_OFFER),
    (3, APPFLOOD_AFFILIATE,"hide", AF_TYPE_DIRECT, PERMISSION_CONFIGURE_DIRECT_OFFER),
    (4, NOT_DIRECT_MASSIVAL, "show", AF_TYPE_NORMAL, PERMISSION_CONFIGURE_MASSIVAL_OFFER),
]

def _list2dict(_list):
    result = {}
    for _info in _list:
        _id, name, op, af_type, pt = _info
        result[_id] = {
            "af_name" : name,
            "direct_type" : _id,
            "op" : op,
            "af_type" : af_type,
            "pt" : pt,
        }
    return result

AFFILIATE_DICT = _list2dict(AFFILIATE_LIST)

