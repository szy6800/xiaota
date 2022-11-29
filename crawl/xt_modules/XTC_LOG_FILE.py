# encoding: UTF-8
from __future__ import division
import os
import time
import sys
import logging
import requests
import datetime
import traceback
import hashlib
import copy
import re
from logging.handlers import TimedRotatingFileHandler
import zlib

#reload(sys)
#sys.setdefaultencoding('utf-8')

from crawl.xt_modules.xtc_base import *

class XTC_LOG_FILE(BaseLog):
    def init(self, conf):
        self.base_dir =  conf.get('log', 'base_path') #os.path.dirname(os.path.realpath(__file__))
        filename = 'crawl_'
        self.file_path = os.path.abspath(os.path.join(self.base_dir, filename))
        self.fname = self.file_path + time.strftime("%Y%m%d", time.localtime()) + '.log'
        self.fp = open(self.fname, 'a+', encoding='utf-8')
        self.fp.close()
        self.task = None

    def log(self, level, info):
        msg = time.asctime() + ":\t" + format(f"pid: {os.getpid()} " + info)
        print(msg, "\n")
        self.fname = self.file_path + time.strftime("%Y%m%d", time.localtime()) + '.log'
        self.fp = open(self.fname, 'a', encoding='utf-8')
        self.fp.write(msg + "\n")
        self.fp.close()
        if not self.task is None and self.task.para['site_id']>0:
            self.task.store.insert_crawl_log(self.task.para['site_id'], level, msg) 
                    
