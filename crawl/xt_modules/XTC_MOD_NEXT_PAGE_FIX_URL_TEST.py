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
import json
from xt_modules.XTC_MOD_NEXT_PAGE_FIX_URL import XTC_MOD_NEXT_PAGE_FIX_URL
from xtc_base import *
from xt_pub_func import *


class XTC_MOD_NEXT_PAGE_FIX_URL_TEST(XTC_MOD_NEXT_PAGE_FIX_URL):


    def get_now_page(self):
        # 更新连续抓取成功页数
        if self.task.env['run_times'] > 1:
            if self.task.env['fail_count'] == 0 and self.order == 'desc':
                if self.task.env['run_times'] > self.re_crawl_page_num:
                    self.succ_pages += 1
                    self.task.para['crawl_para']['succ_pages'] = self.succ_pages

        self.task.logger.debug('%s XTC_MOD_NEXT_PAGE_FIX_URL info=%s' % (
            self.task.site_info, json.dumps(self.task.env['page_result']['info'], indent=2, ensure_ascii=False)))

        if self.order != 'desc':
            return self.task.env['run_times']
        if self.task.env['page_result']['info']['total_page'] > self.total_page:
            add_page = self.task.env['page_result']['info']['total_page'] - self.total_page  # 增加的页数
            if add_page >= 0:
                if add_page == 0:
                    return self.start_page - self.task.env['run_times'] + 1
                self.total_page = self.task.env['page_result']['info']['total_page']
                self.start_page += add_page
                if total_record := int(self.task.env['page_result']['info'].get('record', 0)):  # 总记录数
                    if per_page := int(self.task.env['page_result']['info'].get('per_page', 0)):  # 每页的数据条数
                        r = total_record - self.record
                        if add_page * int(per_page) > r:
                            self.start_page += 1
                        self.record = total_record
            else:
                self.start_page = 0
                self.task.env['run_times'] = 0
        else:
            if self.task.env['page_result']['info'].get('record', 0) > self.record:
                self.task.env['run_times'] -= 1
                self.record = int(self.task.env['page_result']['info'].get('record', 0))
                return self.start_page - self.task.env['run_times'] + 1


        return self.start_page - self.task.env['run_times'] + 1

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

        # 首次运行
        if self.task.env['run_times'] == 1:

            succ_pages = 0
            if 'succ_pages' in self.task.para['crawl_para']:
                succ_pages = self.task.para['crawl_para']['succ_pages']
            else:
                self.task.para['crawl_para']['succ_pages'] = 0

            self.total_page = self.task.env['page_result']['info']['total_page']
            self.record = self.task.env['page_result']['info'].get('record', 0)
            self.start_page = self.total_page - succ_pages + self.re_crawl_page_num  # 多抓self.re_crawl_page_num页
            if self.start_page > self.total_page:
                self.start_page = self.total_page
            self.task.logger.debug('%s XTC_MOD_NEXT_PAGE_FIX_URL set start_page=%d for %d - %d + %d' % (
            self.task.site_info, self.start_page, self.total_page, succ_pages, self.re_crawl_page_num))
            self.succ_pages = succ_pages

        req = {}
        if 'req_para' in self.para:
            for k, v in self.para['req_para'].items():
                req[k] = v

        now_page = self.get_now_page()
        if now_page > 0 and now_page <= self.total_page and len(self.task.env['page_result']['reqs']) > 0:
            self.task.env['page_result']['info']['next_page'] = now_page

            url = get_value(self.para, 'prefix', '')
            url += str(eval(self.para['expr'], None,
                            {'page': now_page, 'para': self.para, 'page_result': self.task.env['page_result']}))
            url += get_value(self.para, 'postfix', '')

            if 'method' in self.para:
                req['method'] = self.para['method']
                if req['method'] == 'post':
                    post_key = get_value(self.para, 'post_key', 'data')
                    req[post_key] = self.para['post_para']
            if 'req_expr' in self.para:
                req['page'] = now_page
                req['para'] = self.para
                req['obj'] = self.task.env['page_result']
                temp = eval(self.para['req_expr'], None, req)
                del req['page']
                del req['para']
                del req['obj']

            req['purl'] = self.task.env['page_result']['reqs'][0]['url']
            req['url'] = get_full_url(url, req['purl'])
            self.task.env['page_result']['next_reqs'].append(req)

        self.task.logger.debug('%s XTC_MOD_NEXT_PAGE_FIX_URL (%s/%s) next_reqs=%s' % (
        self.task.site_info, now_page, self.total_page,
        json.dumps(self.task.env['page_result']['next_reqs'], indent=2, ensure_ascii=False)))
        return {}




