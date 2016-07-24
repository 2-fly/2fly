
import sys
from os import path as osp

sys.dont_write_bytecode = True

cur_path = osp.dirname(osp.realpath(__file__))
parent_path = osp.dirname(cur_path)

sys.path.insert(0, parent_path)


