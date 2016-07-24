#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging

devices = None
search_algorithm = None



def get_device_id(user_agent):
    global devices
    global search_algorithm
    if search_algorithm is None:
        from wurfl import devices as tmp_devices
        from pywurfl.algorithms import TwoStepAnalysis
        devices = tmp_devices
        search_algorithm = TwoStepAnalysis(devices)

    device = None
    try:
        device = devices.select_ua(user_agent, search=search_algorithm)
    except Exception, ex:
        logging.error('failed to get deviceid from: %s %s'%(user_agent, str(ex)))

    if device:
        return '%s %s'%(str(device.brand_name), str(device.model_name))
    else:
        return None
    #return 'SUNGSUM GALAXY S4'



def get_device_info(user_agent):
    global devices
    global search_algorithm
    if search_algorithm is None:
        from wurfl import devices as tmp_devices
        from pywurfl.algorithms import TwoStepAnalysis
        devices = tmp_devices
        search_algorithm = TwoStepAnalysis(devices)

    device = None
    try:
        device = devices.select_ua(user_agent, search=search_algorithm)
    except Exception, ex:
        logging.error('failed to get deviceid from: %s %s'%(user_agent, str(ex)))

    if device:
        return {
            'model_name' : device.model_name,
            'brand_name' : device.brand_name,
            'devid' : device.devid,
            #'devua' : device.devua,
            'devua' : user_agent,
            'device_os' : device.device_os,
            'device_os_version' : device.device_os_version,
            'mobile_browser' : device.mobile_browser,
            'mobile_browser_version' : device.mobile_browser_version,
        }
    else:
        return {
            'model_name' : '',
            'brand_name' : '',
            'devid' : '',
            #'devua' : device.devua,
            'devua' : user_agent,
            'device_os' : '',
            'device_os_version' : '',
            'mobile_browser' : '',
            'mobile_browser_version' : '',
        }



if __name__ == '__main__':
    a = u'Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/KRT16M) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36'
    print get_device_id(a)
    print get_device_info(a)

