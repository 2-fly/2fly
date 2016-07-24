#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import socket
import time
import logging
from os import path as osp


class MBLogFile(object):
    def __init__(self, directory, basename=''):
        self.hostname = socket.gethostname()
        self.directory = directory
        self.basename = basename
        self.filename = ''
        self.fd = None
        self.check_filename()

    def check_filename(self, ts=None):
        if ts is None:
            now = datetime.datetime.now()
        else:
            now = datetime.datetime.fromtimestamp(ts)

        date_str = now.strftime('%Y%m%d%H')
        filename = '%s_%s_%s'%(self.hostname, date_str, self.basename)
        filename = osp.join(self.directory, filename)
        if self.filename != filename:
            self.filename = filename
            if self.fd:
                self.fd.close()
                self.fd = None

            self.fd = open(self.filename, 'a')

    def write(self, s, ts=None):
        if ts is None:
            start = time.time()
        else:
            start = ts
        self.check_filename(start)
        self.fd.write(s)
        diff = int((time.time() - start)*1000)
        if diff > 200:
            logging.error('MBLogFile write too slow %d ms'%diff)


    def flush(self):
        start = time.time()
        self.fd.flush()
        diff = int((time.time() - start)*1000)
        if diff > 200:
            logging.error('MBLogFile flush too slow %d ms'%diff)

    def close(self):
        self.fd.close()


