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
from http.server import HTTPServer, BaseHTTPRequestHandler


sys.path.append("./xt_lib")
sys.path.append("./xt_modules")

from xtc_base import *
from JsonServer import *
from xt_pub_func import *

def work_func(paras, handle):
    global g_frame
    g_frame.logger.clear()

    if 'site_para' in paras:
        site_para = json.loads(paras['site_para'])
        print("\n\n\n\nbegin deal")
        task = {}
        task['site_id'] = 0
        task['state_info'] = ''
        task['crawl_interval'] = 86400
        task['next_crawl_time'] = datetime.datetime.now()
        task['crawl_para'] = {}
        task['site_script'] = ''
        task['site_config'] = site_para

        print('work_func', task)
        g_frame.test(task)
        result = {'logs':g_frame.logger.log_buff}
    elif 'rule' in paras:
        req = {}
        req['url'] = paras['url']
        req['text'] = paras['text']
        rule = json.loads(paras['rule'])
        result = json.loads(paras['result'])
        pick_data(req, rule, result)
    else:
        print("para=", paras)
        return {'code':0, 'msg':'not find site_para'}
 
    return {'code':0, 'msg':'success', 'result':result}

class MyJsonServerHandler(JsonServerHandler):
    def _deal(self, paras):
        #print("in deal paras=%s"%(paras))
        try:
            result = work_func(paras, self)
        except Exception as err:
            print(traceback.format_exc())
            result = {"code":-100, 'msg':'fail', 'result': str(traceback.format_exc())}
        #print("result=%s"%(result))
        self.send_result(bytes( json.dumps(result),  encoding = "utf8"))


def signal_handler(signalnum, frame):
    global httpd
    print("recv signal %s %s"%(signalnum, frame))
    httpd.socket.close()


if __name__ == '__main__':
    #启动监听服务
    if len(sys.argv) < 2 :
        print("Please input like:\n\t" + sys.argv[0] + " config_file\n")
        exit()

    conf = configparser.ConfigParser()
    conf.read(sys.argv[1])

    host = conf.get('server', 'host')
    port = conf.getint('server', 'port')

    frame_name = conf.get('frame', 'name')

    print("begin init frame ", frame_name)
    g_modules = init_g_modules()
    g_frame = LoadXTClass(frame_name)(conf)
    g_frame.g_modules = g_modules
    g_frame.run_flag = True

    print("begin call frame.init")
    g_frame.init()


    print("start server")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    Handler = MyJsonServerHandler
    httpd = HTTPServer((host, port), Handler)
    try:
        httpd.serve_forever()
    except:
        print("run server error")
        sys.exit(-1)
    httpd.shutdown()

