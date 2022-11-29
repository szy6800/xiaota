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

from .xtc_base import *
from crawl.xt_lib.xt_pub_func import *

class XTC_MOD_NEXT_PAGE_URL(BaseMOD):
    def init(self, task):
        self.task = task
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

        if len(self.task.env['page_result']['next_reqs']) > 0:
            req = self.task.env['page_result']['next_reqs'][0]
            req['url'] = get_full_url(req['url'], req['purl'])
            #if req['url'] == self.task.env['page_result']['reqs'][0]['url']:
            #    self.task.env['page_result']['next_reqs'] = []
        self.task.logger.debug('%s XTC_MOD_NEXT_PAGE_URL next_reqs=%s'%(self.task.site_info, json.dumps(self.task.env['page_result']['next_reqs'], indent=2, ensure_ascii=False)))
        return {}


        return {}
        
    #结束    
    def end(self):
        return {}
                        
