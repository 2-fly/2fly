#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import logging

import ujson as json
from flask import Flask, request

import init_env
import settings


#logging.basicConfig(stream = sys.stderr)
app = Flask(__name__)
app.debug = settings.debug



def get_autoscale_instance(data):
    from pprint import pprint as pp
    info = json.loads(data)
    if info['Type'] != 'Notification' or 'Auto Scaling' not in info['Subject']:
        return

    msg_obj = json.loads(info['Message'])
    #pp(msg_obj)
    return msg_obj['EC2InstanceId']


def get_cpulow_group(data):
    from pprint import pprint as pp
    info = json.loads(data)
    if info['Type'] != 'Notification' or 'cpulow' not in info['Subject']:
        return

    msg_obj = json.loads(info['Message'])
    #pp(msg_obj)
    return msg_obj['Trigger']['Dimensions'][0]['value']



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
    return ips



def handle_cpulow(data, low_group):
    from pprint import pprint as pp
    info = json.loads(data)

    ips = []
    for obj in info['Reservations']:
        instance = obj['Instances'][0]
        tag  = instance['Tags'][0]
        #print tag['Value'], tag['Key'], instance['InstanceId'], instance['State']
        #if obj['Instances'][0]['Tags'][0]['Value'] != low_group:
        if instance['State']['Name'] != 'running':
            continue
        ips.append((instance['InstanceId'], instance['PrivateIpAddress']))

    return ips


def get_describe_instances():
    s = os.popen('aws ec2 describe-instances').read()
    return s


new_instance_data = None
with open('data/newscale', 'r') as f:
    new_instance_data = f.read()

ccc = None
with open('data/cpulow2', 'r') as f:
    ccc = f.read()

fff = None
with open('data/describe', 'r') as f:
    fff = f.read()


print '-'*80
new_instance_id = get_autoscale_instance(new_instance_data)
#fff = get_describe_instances()
ips = handle_new_instance(fff, new_instance_id)
print 'new_instance_id: ', new_instance_id
print 'ips: ', ips



print '-'*80
low_group = get_cpulow_group(ccc)
#fff = get_describe_instances()
ips = handle_cpulow(fff, low_group)
print 'low_group: ', low_group
print 'ips: ', ips

xxxx


log_file = open('as.log', 'a')


def get_request_args():
    d1 = request.args.to_dict()
    d2 = request.form.to_dict()
    d2.update(d1)
    return d2



@app.route('/deviceinfo', methods=['POST', 'GET'])
def handle_deviceinfo():
    session_info = get_request_args()
    user_agent = session_info.get('ua', u'')
    device_info = get_device_info(user_agent)

    ip = session_info.get('ip', '')
    country_name, country, city = ipquery.get_info(ip)
    isp = ispquery.get_isp(ip)
    device_info['country_name'] = country_name
    device_info['country'] = country
    device_info['city'] = city
    device_info['isp'] = isp
    return json.dumps(device_info)




@app.route('/testautos/', methods=['POST', 'GET'])
def handle_as():
    data = request.get_data()
    log_file.write(data+'\n')
    log_file.flush()



if __name__ == '__main__':
    app.run(settings.bind_ip, settings.bind_port)


