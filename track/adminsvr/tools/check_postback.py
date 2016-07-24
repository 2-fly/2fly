#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import init_env

class CheckPostback(object):
    def __init__(self, filename, cid_path, pb_path, time_list=None):
        time_list = time_list or ""
        self._filename = filename
        self._cid_path = cid_path
        self._pb_path = pb_path 
        self._pb_map = {} 
        self._path_cid_map = {}
        self._path_pb_map = {}
        self.time_list = time_list.split(",")

    def load_file(self):
        f = open(self._filename, "r")
        count = 0
        valid = 0
        for line in f:
            cid = line[:-1]
            if len(cid) < 32:
                valid += 1
            if cid not in self._pb_map:
                self._pb_map[cid] = 0
            self._pb_map[cid] += 1
            count += 1
        f.close()
        print "read file is done.file count(%s), map(%s), valid(%s)" % (count, len(self._pb_map), valid)

    def load_file_xlx(self):
        import xlrd
        filename = self._filename
        book = xlrd.open_workbook(filename)
        count = 0
        valid = 0
        for idx in xrange(0, book.nsheets, 1):
            sh = book.sheet_by_index(idx)
            for rows in xrange(1, sh.nrows,1):
                cid = sh.cell_value(rows, 5).strip()
                cid = str(cid)
                if len(cid) < 32:
                    valid += 1
                if cid not in self._pb_map:
                    self._pb_map[cid] = 0
                self._pb_map[cid] += 1
                count += 1
        print "read file is done.file count(%s), map(%s), valid(%s)" % (count, len(self._pb_map), valid)
        f = open("pb.txt", "w")
        for k, v in self._pb_map.items():
            s = "%s\n" % (k)
            f.write(s)
        f.close()

    def __check_is_match_date_file(self, filename):
        for t in self.time_list:
            if filename.find(t) >= 0:
                return True
        return False

    def load_cid_path(self):
        path = self._cid_path
        filelist = []
        base_list = os.listdir(path)
        for i in xrange(0, len(base_list)):
            if not self.__check_is_match_date_file(base_list[i]):
                continue
            p = os.path.join(path, base_list[i])
            if os.path.isfile(p):
                filelist.append(p)

        count = 0
        valid = 0
        for f in filelist:
            fi = open(f, "r")
            fi_count = 0
            for line in fi:
                l = line.split(",")
                cid = str(l[1].strip())
                if len(cid) < 32:
                    valid += 1
                count += 1
                fi_count += 1
                if cid not in self._path_cid_map:
                    self._path_cid_map[cid] = 0
                self._path_cid_map[cid] += 1
            fi.close()
            print "fi_count:", fi_count, f
        print "read cid path file is done.file count(%s), map(%s), valid(%s)" % (count, len(self._path_cid_map), valid)

    def load_pb_path(self):
        path = self._pb_path
        filelist = []
        base_list = os.listdir(path)
        for i in xrange(0, len(base_list)):
            if not self.__check_is_match_date_file(base_list[i]):
                continue
            p = os.path.join(path, base_list[i])
            if os.path.isfile(p):
                filelist.append(p)

        count = 0
        valid = 0
        for f in filelist:
            fi = open(f, "r")
            for line in fi:
                l = line.split(",")
                cid = str(l[0].strip())
                if len(cid) < 32:
                    valid += 1
                count += 1
                if cid not in self._path_pb_map:
                    self._path_pb_map[cid] = 0
                self._path_pb_map[cid] += 1
            fi.close()
        print "read postback path file is done.file count(%s), map(%s), valid(%s)" % (count, len(self._path_pb_map), valid)

    def _save_path_cid(self):
        f = open("pb_path.txt", "w")
        for k, v in self._path_pb_map.items():
            s = "%s,%s\n" % (k,v)
            f.write(s)
        f.close()

    def _do_pb_check(self):
        total = len(self._pb_map)
        miss_list = []
        count = 0
        for cid, num in self._pb_map.items():
            if cid in self._path_pb_map:
                count += 1
            else:
                miss_list.append(cid)
        rate = count * 1.0 / total if total != 0 else 0.0
        print "postback check result:total(%s), count(%s), rate(%s)" % (total, count, rate)
        print "miss_list:", len(miss_list)
        ##print miss_list

    def _do_cid_check(self):
        total = len(self._pb_map)
        miss_list = []
        count = 0
        for cid, num in self._pb_map.items():
            if cid in self._path_cid_map:
                count += 1
            else:
                miss_list.append(cid)

        rate = count * 1.0 / total if total != 0 else 0.0
        print "cid check result:total(%s), count(%s), rate(%s)" % (total, count, rate)
        print "miss_list:", len(miss_list)
        ##print miss_list

    def check(self):
        self.load_file()
        self.load_pb_path()
        self.load_cid_path()
        self._do_pb_check()
        self._do_cid_check()
        #self._save_path_cid()


def check_file_diff(f1, f2):
    def get_file(f1):
        f = open(f1, "r")
        f1_map = {}
        for l in f:
            cid = l[:-1]
            f1_map[cid] = 1
        f.close()
        return f1_map
    f1_map = get_file(f1)
    f2_map = get_file(f2)
    count = 0
    miss_list = []
    for k, v in f1_map.items():
        if k not in f2_map:
            count += 1
            miss_list.append(k)
    print count
    print miss_list

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print "python check_postback.py filename cid_path pb_path time_list(20160116,20160117)"
        exit(1)
    filename = sys.argv[1]
    cid_path = sys.argv[2]
    pb_path = sys.argv[3]
    time_list = sys.argv[4]
    obj = CheckPostback(filename, cid_path, pb_path, time_list)
    obj.check()
    
