# -*- coding: utf-8 -*-

'''
#=============================================================================
#
#     FileName: pay_helper.py
#         Desc: 用来帮助做支付回调发货协议的签名验证
#
#       Author: open.qq.com
#
#      Created: 2012-08-28 16:49:33
#      Version: 3.0.1
#      History:
#               3.0.1 | dantezhu | 2012-08-28 16:49:33 | support cpay callback sig verifictaion.
#
#=============================================================================
'''

import re
import urllib
import binascii
import hashlib
import hmac

def pay_rep_value(src):
    """
    将排序后的参数(key=value)用&拼接起来，并进行URL编码”之前，需对value先进行一次编码
    （编码规则为：除了 0~9 a~z A~Z !*() 之外其他字符按其ASCII码的十六进制加%进行表示，例如“-”编码为“%2D”）
    """
    src = str(src)
    dst = ''
    #pattern = re.compile(r'[0-9a-zA-Z!*()]')
    for it in src:
        #if re.match(r'[0-9a-zA-Z!*()]', it):
        #if pattern.match(it):
        #if it.isalnum() or (it == '!') or (it == '*') or (it == '(') or (it == ')'):
        if ('0' <= it <= '9') or ('A' <= it <= 'Z') or ('a' <= it <= 'z') or (it == '!') or ('(' <= it <= '*'):
            #找到了
            dst += it
        else:
            dst += '%%%02X' % ord(it)

    return dst

def mk_soucrce(method, url_path, params):
    str_params = urllib.quote("&".join(k + "=" + pay_rep_value(params[k]) for k in sorted(params.keys())), '')

    source = '%s&%s&%s' % (
        method.upper(),
        urllib.quote(url_path,''),
        str_params
        )

    return source


def hmac_sha1_sig(method, url_path, params, secret):
    source = mk_soucrce(method, url_path, params)
    hashed = hmac.new(secret, source, hashlib.sha1)
    return binascii.b2a_base64(hashed.digest())[:-1]

def verify_pay_callback_sig(appkey, method, url_path, params):
    """
    验证签名
    """
    input_sig = params.pop('sig', None)

    sig = hmac_sha1_sig(method, url_path, params, appkey+'&')

    return input_sig == sig
