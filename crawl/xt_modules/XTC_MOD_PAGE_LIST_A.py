# encoding: UTF-8
from __future__ import division
import os
import time
import sys
import logging
import datetime
import traceback
import hashlib
import copy
import re
import requests
import html
from bs4 import BeautifulSoup
import bs4
import lxml
from lxml import etree

from xtc_base import *
from crawl.xt_lib.xt_pub_func import *

class XTC_MOD_PAGE_LIST_A(BaseMOD):
    def init(self, task):
        self.task = task
        return {}
    
    def run(self):
        self.task.env['page_result']['para'] = self.para
        
        #首次运行
        if self.task.env['run_times'] == 1:
            if 'req' in self.para:
                self.task.env['page_result']['reqs'].append(self.para['req'])
            if 'reqs' in self.para:
                for req in self.para['reqs']:
                    self.task.env['page_result']['reqs'].append(req)
        else:
            self.task.env['page_result']['reqs'] = self.task.env['page_result']['next_reqs']
            self.task.env['page_result']['next_reqs'] = []

        self.task.logger.debug('%s XTC_MOD_PAGE_LIST_A reqs=%s'%(self.task.site_info, json.dumps(self.task.env['page_result']['reqs'], indent=2, ensure_ascii=False)))

        if 'module_expr' in self.para:
            eval(self.para['module_expr'], None, {'obj':self.task.env['page_result']})
            
        for i in range(100):
            if i >= len(self.task.env['page_result']['reqs']):
                break
            req = self.task.env['page_result']['reqs'][i]

            if 'req_expr' in req:
                eval(req['req_expr'], None, {'req':req, 'obj':self.task.env['page_result']})

            res = self.task.request_url(req, self.para)
            if res.status_code != 200:
                self.task.logger.debug("%s XTC_MOD_PAGE_LIST_A get fail %s %s"%(self.task.site_info, res.status_code, res.url))
                return {}

            req['text'] = res.text
            req['content'] = res.content
            self.task.env['page_result']['now_req'] = req
            if 'rule' in self.para:
                pick_data(req, self.para['rule'], self.task.env['page_result'])
            if 'rules' in self.para:
                for rule in self.para['rules']:
                    pick_data(req, rule, self.task.env['page_result'])

        self.task.logger.debug('%s XTC_MOD_PAGE_LIST_A docs=%s'%(self.task.site_info, json.dumps(self.task.env['page_result']['docs'], indent=2, ensure_ascii=False)))

        return {}
        
    #结束    
    def end(self):
        return {}
                        
