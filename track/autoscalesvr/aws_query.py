#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
from datetime import datetime

import ujson as json

import settings


def get_autoscale_instance(data):
    from pprint import pprint as pp
    info = json.loads(data)
    if info['Type'] != 'Notification' or 'Auto Scaling' not in info['Subject']:
        return

    msg_obj = json.loads(info['Message'])
    #pp(msg_obj)
    return msg_obj['EC2InstanceId']


def handle_new_instance(data, instance_id):
    from pprint import pprint as pp
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


def get_autoscaling_instances():
    s = os.popen('aws autoscaling describe-auto-scaling-instances').read()
    try:
        data = json.loads(s)
    except Exception, ex:
        raise ex

    instances = []
    for obj in data['AutoScalingInstances']:
        if obj['AutoScalingGroupName'] == settings.autoscale_groupname:
            if obj['InstanceId'] not in instances:
                instances.append(obj['InstanceId'])


    s = os.popen('aws ec2 describe-instances').read()
    try:
        data = json.loads(s)
    except Exception, ex:
        raise ex

    ips = []
    for instance_id in instances:
        for obj in data['Reservations']:
            instance = obj['Instances'][0]
            if 'InstanceId' not in instance or 'LaunchTime' not in instance or 'PrivateIpAddress' not in instance:
                continue

            if instance['InstanceId'] != instance_id:
                continue

            # "LaunchTime": "2015-09-01T04:19:20.000Z"
            dt = datetime.strptime(instance['LaunchTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
            ips.append((instance['InstanceId'], instance['PrivateIpAddress'], dt))

    ips.sort(key=lambda v:v[2], reverse=True)
    ips = ['%s %s'%(x, y) for x, y, z in ips]

    return '\n'.join(ips)


if __name__ == '__main__':
    cmd = sys.argv[1]

    if cmd == 'get_ip':
        instanceid = sys.argv[2]
        fff = get_describe_instances()
        ip = handle_new_instance(fff, instanceid)
        print ip
    elif cmd == 'get_autoscale':
        print get_autoscaling_instances()
    else:
        print 'FAIL\ncommand not found:%s'%cmd

