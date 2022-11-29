# encoding: UTF-8
from __future__ import division
import json
import sys
import os
import timeit
import time
import types
import csv
import logging
import requests
import datetime
import traceback
import hashlib
import copy
import signal
import configparser

sys.path.append("./xt_lib")
sys.path.append("./xt_modules")

from crawl.xt_modules.xtc_base import *

def signal_handler(signalnum, frame):
    global g_frame
    print("recv signal %s %s"%(signalnum, frame))
    g_frame.run_flag = False
    if not g_frame.m_task is None:
        g_frame.m_task.run_flag = False

# if len(sys.argv) < 2 :
#     print("Please input like:\n\t" + sys.argv[0] + " config_file\n")
#     exit()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

conf = configparser.ConfigParser()
conf.read(r'E:\practise\xiaota\crawl\crawl.conf')

frame_name = conf.get('frame', 'name')

print("begin init frame ", frame_name)
g_modules = init_g_modules()
g_frame = LoadXTClass(frame_name)(conf)
g_frame.g_modules = g_modules
g_frame.run_flag = True

print("begin call frame.init")
g_frame.init()

print("begin call frame.run")
g_frame.run()

print("begin call frame.end")
g_frame.end()

print("end")

