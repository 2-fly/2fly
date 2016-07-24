#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import logging
from pprint import pprint as pp
from functools import wraps

import ujson as json
from flask import Flask, request

import init_env
import settings
from commlib.db.redis_helper import CacheTable

#logging.basicConfig(stream = sys.stderr)
app = Flask(__name__)
app.debug = settings.debug


redis_cli = CacheTable(settings.redis_as_db, host=settings.redis_host, port=settings.redis_port)

increase_exe = '/home/ec2-user/massival/autoscalesvr/remote/increase.sh'
decrease_exe = '/home/ec2-user/massival/autoscalesvr/remote/decrease.sh'


def parse_msgid(data):
    info = json.loads(data)
    return info['MessageId']


def get_autoscale_instance(data):
    info = json.loads(data)
    if info['Type'] != 'Notification' or 'Auto Scaling' not in info['Subject']:
        return

    msg_obj = json.loads(info['Message'])
    #pp(msg_obj)
    return msg_obj['EC2InstanceId']


def handle_new_instance(data, instance_id):
    info = json.loads(data)
    ips = []
    for obj in info['Reservations']:
        instance = obj['Instances'][0]
        if instance['InstanceId'] != instance_id:
            continue

        #print '-'*50
        ips.append(instance['PrivateIpAddress'])
        #pp(instance['InstanceId'])
    ip = ('').join(ips)
    return ip


def get_describe_instances():
    s = os.popen('aws ec2 describe-instances').read()
    return s


def add_msgid(msgid, data):
    global redis_cli
    redis_cli.setex(msgid, data, settings.redis_as_expire)


def get_msgid(msgid):
    global redis_cli
    return redis_cli.get(msgid)


log_file = open('as.log', 'a')


def base_checker(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        data = request.get_data()
        log_file.write(data+'\n')
        log_file.flush()

        msg_id = parse_msgid(data)
        if get_msgid(msg_id):
            return 'ALREADY'

        add_msgid(msg_id, data)

        return func(*args, **kwargs)
    return decorated_function



@app.route('/decrease/', methods=['POST', 'GET'])
@base_checker
def handle_decrease():
    data = request.get_data()
    os.popen('bash %s >> /var/log/uwsgi/decrease.log 2>&1 &'%decrease_exe)
    return 'OK'



@app.route('/increase/', methods=['POST', 'GET'])
@base_checker
def handle_increase():
    data = request.get_data()

    new_instance_id = get_autoscale_instance(data)
    if new_instance_id is None or not new_instance_id:
        return 'ERROR ID'

    fff = get_describe_instances()
    ip = handle_new_instance(fff, new_instance_id)

    os.popen('bash %s %s %s >> /var/log/uwsgi/increase.log 2>&1 &'%(increase_exe, new_instance_id, ip))
    return 'OK'



if __name__ == '__main__':
    app.run(settings.bind_ip, settings.bind_port)


