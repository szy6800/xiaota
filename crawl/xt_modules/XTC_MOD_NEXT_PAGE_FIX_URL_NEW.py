# encoding: UTF-8
from __future__ import division
from operator import methodcaller
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

from .xtc_base import *
from crawl.xt_lib.xt_pub_func import *

class XTC_MOD_NEXT_PAGE_FIX_URL_NEW(BaseMOD):
    def init(self, task):
        self.task = task
        self.order = get_value(self.para, 'order', 'desc')
        self.total_page = 0
        self.start_page = 0
        self.re_crawl_page_num = int(get_value(self.para, 're_crawl_page_num', 10))
        return {}
    
    def run(self):
        self.task.env['page_result']['next_reqs'] = []
        self.task.env['page_result']['para'] = self.para
        
        for data in self.task.env['page_result']['reqs']:
            self.task.env['page_result']['now_req'] = data
            if 'rule' in self.para:
                pick_data(data, self.para['rule'], self.task.env['page_result'])
            if 'rules' in self.para:
                for rule in self.para['rules']:
                    pick_data(data, rule, self.task.env['page_result'])


        #首次运行
        if self.task.env['run_times'] == 1:
            succ_pages = 0
            if 'succ_pages' in self.task.para['crawl_para']:
                succ_pages = self.task.para['crawl_para']['succ_pages']
            else:
                self.task.para['crawl_para']['succ_pages'] = 0

            self.total_page = self.task.env['page_result']['info']['total_page']

            self.start_page = self.total_page - succ_pages + self.re_crawl_page_num #多抓self.re_crawl_page_num页
            if self.start_page > self.total_page:
                self.start_page = self.total_page
            self.task.logger.debug('%s XTC_MOD_NEXT_PAGE_FIX_URL_NEW set start_page=%d for %d - %d + %d'%(self.task.site_info, self.start_page, self.total_page , succ_pages , self.re_crawl_page_num))
        else:
            #更新连续抓取成功页数
            if self.task.env['fail_count'] == 0 and self.order == 'desc':
                #self.total_page - now_page
                temp_succ_page = self.total_page - (self.start_page - self.task.env['run_times'] + 1)
                if self.task.para['crawl_para']['succ_pages'] < temp_succ_page:
                    self.task.para['crawl_para']['succ_pages'] = temp_succ_page


        self.task.logger.debug('%s XTC_MOD_NEXT_PAGE_FIX_URL_NEW info=%s'%(self.task.site_info, json.dumps(self.task.env['page_result']['info'], indent=2, ensure_ascii=False)))

        req = {}
        if 'req_para' in self.para:
            for k, v in self.para['req_para'].items():
                req[k] = v

        if self.order == 'desc':
            now_page = self.start_page - self.task.env['run_times'] + 1
        else:
            now_page = self.task.env['run_times']

        if now_page > 0 and now_page <= self.total_page and len(self.task.env['page_result']['reqs']) > 0:
            self.task.env['page_result']['info']['next_page'] = now_page
            
            for data in self.task.env['page_result']['reqs']:
                self.task.env['page_result']['now_req'] = data
                if 'next_rule' in self.para:
                    pick_data(data, self.para['next_rule'], self.task.env['page_result'])
                if 'next_rules' in self.para:
                    for rule in self.para['next_rules']:
                        pick_data(data, rule, self.task.env['page_result'])

            if 'expr' in self.para:
                req = eval(self.para['expr'], None, {'page':now_page, 'para':self.para, 'page_result':self.task.env['page_result']})
                if not req is None:
                    self.task.env['page_result']['next_reqs'].append(req)

        self.task.logger.debug('%s XTC_MOD_NEXT_PAGE_FIX_URL_NEW (%s/%s) next_reqs=%s'%(self.task.site_info, now_page,self.total_page,json.dumps(self.task.env['page_result']['next_reqs'], indent=2, ensure_ascii=False)))
        return {}
        
    #结束    
    def end(self):
        return {}
                        

