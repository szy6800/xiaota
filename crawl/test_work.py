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

if len(sys.argv) < 2 :
    print("Please input like:\n\t" + sys.argv[0] + " config_file\n")
    exit()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

conf = configparser.ConfigParser()
conf.read(sys.argv[1])

frame_name = conf.get('frame', 'name')

print("begin init frame ", frame_name)
g_modules = init_g_modules()
g_frame = LoadXTClass(frame_name)(conf)
g_frame.g_modules = g_modules
g_frame.run_flag = True

g_frame.init()

##################################################################
task = {}
task['site_id'] = 0     #这个地方一定得是0， 不要修改
task['state_info'] = ''
task['crawl_interval'] = 86400
task['next_crawl_time'] = datetime.datetime.now()
task['crawl_para'] = {}
task['site_script'] = ''

####下面把配置参数直接贴进去
task['site_config'] = {
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": "福建"
  },
  "stop_filter": "run_times>1",
  "url_key_expr": "url",
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "https://fzsggzyjyfwzx.cn/jyxxzfcg/index.jhtml"
      },
      "rule": {
        "pick": {
          "type": "soup",
          "pattern": ".article-list3-t",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "docs.+.url",
                "expr": "values['soup'].a['href']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.purl",
                "expr": "obj['now_req']['url']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.title",
                "expr": "values['soup'].a.text.strip()"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "values['soup'].div.text.strip()"
              }
            ]
          }
        }
      }
    }
  },
  "next_page": {
    "module_name": "XTC_MOD_NEXT_PAGE_URL",
    "module_para": {
      "rule": {
        "pick": {
          "type": "soup",
          "pattern": "a:-soup-contains(下一页)",
          "sub": {
            "pick": {
              "type": "re",
              "pattern": "onclick=\"location.href='(.*)';\"",
              "sub": {
                "actions": [
                  {
                    "type": "set_value",
                    "key": "next_reqs.+.url",
                    "expr": "values['values']"
                  },
                  {
                    "type": "set_value",
                    "key": "next_reqs.-1.purl",
                    "expr": "obj['now_req']['url']"
                  }
                ]
              }
            }
          }
        }
      }
    }
  },
  "content": {
    "module_name": "XTC_MOD_CONTENT_STD",
    "module_para": {}
  }
}

g_frame.test(task)

g_frame.end()

print("end")

