# encoding: UTF-8
from __future__ import division
import os
import sys
import time
import logging
import traceback
import urllib
import json
import threading
import copy
from bs4 import BeautifulSoup
import bs4
import lxml
from lxml import etree

import requests
import httpx

from xtc_base import *
from crawl.xt_lib.xt_pub_func import *

class XTC_TASK_STD(BaseTask):
    def init(self, logger, store):
        self.logger = logger
        self.store = store
        self.step_info = {}
        self.state_info = ''
        self.site_info = 'site_id=' + str(self.para['site_id']) + ' '
        self.run_flag = True

        if 'site_script' in self.para and (not self.para['site_script'] is None):
            if len(self.para['site_script']) > 0:
                set_site_script(self.para['site_script'])

        self.max_allow_fail_count = int(get_value(self.para['site_config'], 'max_allow_fail_count', 0))
        self.max_content_size = int(get_value(self.para['site_config'], 'max_content_size', 1000000))
        self.timeout = int(get_value(self.para['site_config'], 'timeout', 60))

        self.dup_flag = int(get_value(self.para['site_config'], 'dup_flag', 0))

        self.hash_mod = get_value(self.para['site_config'], 'hash_mod')
        self.proxies = self.store.get_proxy(get_value(self.para['site_config'], 'proxy_key'))
        
        if 'http2' in self.para['site_config']:
            self.req = httpx.Client(http2=True)
        else:
            self.req = requests.session()

        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.logger.debug("%s begin in task init modules %s %s"%(self.site_info, self.hash_mod, self.proxies))

        self.request_interval = get_value(self.para['site_config'], 'request_interval', 5)
        self.request_retry_times = get_value(self.para['site_config'], 'request_retry_times', 3)
        for k, v in get_value(self.para['site_config'], 'request_headers', {}).items():
            self.headers[k] = v

        self.m_init = InitModuleFromPara(self.para['site_config'], 'init', BaseMOD)
        self.m_page_list = InitModuleFromPara(self.para['site_config'], 'page_list', BaseMOD)
        self.m_next_page = InitModuleFromPara(self.para['site_config'], 'next_page', BaseMOD)
        self.m_content = InitModuleFromPara(self.para['site_config'], 'content', BaseMOD)

        self.m_init.init(self)
        self.m_page_list.init(self)
        self.m_next_page.init(self)
        self.m_content.init(self)

        self.logger.debug("%s end in task init modules "%(self.site_info))

        return {}
        

    def request_url(self, req, para=None):
        if 'no_request' in req:
            res = BaseMOD({})
            res.status_code = 200
            res.url = get_value(req, 'url', '')
            res.text = get_value(req, 'text', '')
            res.content = get_value(req, 'content', res.text)
            res.headers = {}
            res.headers['Content-Type'] = get_value(req, 'Content-Type', 'text/html; charset=utf-8')
            return res

        headers = self.headers.copy()

        url = get_value(req, 'url', '')
        if url == '':
            self.logger.debug("%s XTC_TASK_STD get url is None"%(self.site_info))
            raise KeyError('get url is None')

        purl = get_value(req, 'purl', '')
        if purl != '':
            headers['Referer'] = purl
        req['url'] = get_full_url(req['url'], purl)
        self.logger.debug("%s XTC_TASK_STD request_url %s"%(self.site_info, req['url']))
        #print('request_url url=',req['url'], ' purl=', purl)
        self.step_info['req_url'] = req['url']

        for k, v in get_value(req, 'headers', {}).items():
            headers[k] = v

        files = get_value(req, 'files', None)

        method = get_value(req, 'method', 'get')

        req_paras = {'headers':headers}
        req_paras['timeout'] = int(get_value(req, 'timeout', self.timeout))

        if not self.proxies is None:
            req_paras['proxies'] = self.proxies
        if 'proxies' in req:
            req_paras['proxies'] = req['proxies']

        if 'verify' in self.para['site_config']:
            req_paras['verify'] = self.para['site_config']['verify']
        if 'verify' in req:
            req_paras['verify'] = req['verify']

        if 'params' in self.para['site_config']:
            req_paras['params'] = self.para['site_config']['params']
        if 'params' in req:
            req_paras['params'] = req['params']

        if 'cookies' in self.para['site_config']:
            req_paras['cookies'] = self.para['site_config']['cookies']
        if 'cookies' in req:
            req_paras['cookies'] = req['cookies']
            
        if not files is None:
            req_paras['files'] = files
        if method == 'post':
            if 'json' in req:
                req_paras['json'] = req['json']
            else:
                req_paras['data'] = req['data']

        for i in range(self.request_retry_times):
            try:
                time.sleep(self.request_interval)
                if method == 'post':
                    res = self.req.post(req['url'], **req_paras)
                else:
                    print('req_paras=', req_paras)
                    res = self.req.get(req['url'], **req_paras)
                if res.status_code == 200:
                    break
            except Exception as ex:
                self.logger.error(self.site_info + traceback.format_exc())
                if i == self.request_retry_times -1:
                    raise
        
        ctype = get_content_type(res, self.max_content_size, req)
        self.logger.debug("%s end get %s %s %s %s"%(self.site_info, res.status_code, ctype, len(res.content), req['url']))

        if ctype == 'text':
            encoding = get_value(req, 'encoding', None)
            charset = get_html_charset(res.text)
            if encoding is None:
                if (not charset is None) and charset != '':
                    res.encoding = charset
            elif encoding != '':
                res.encoding = encoding
            self.step_info['req_result_text'] = res.text[:2048]
        return res

    def run(self):
        self.m_init.run()

        self.logger.debug("%s in task run"%(self.site_info))
        #开始抓取列表页
        self.env['dup_url'] = 0
        self.env['run_times'] = 0
        self.env['fail_count'] = 0
        self.env['success_count'] = 0
        self.env['total_count'] = 0
        self.env['page_result'] = {'para':self.para}
        self.env['page_result']['reqs'] = []
        self.env['page_result']['next_reqs'] = []
        while self.run_flag:
            self.env['run_times'] += 1
            self.env['page_result']['docs'] = []

            self.step_info = {}

            
            self.m_page_list.run()
            self.m_next_page.run()

            #开始对公告内容进行抓取
            for doc in self.env['page_result']['docs']:
                doc['site_id'] = self.para['base_site_id']
                doc['sub_id'] = self.para['site_id']
                if 'url_key_expr' in self.para['site_config']:
                    doc['url_key'] = calc_md5(eval(self.para['site_config']['url_key_expr'], None, doc))
                else:
                    doc['url_key'] = calc_md5(get_full_url(doc['url'], get_value(doc, 'purl', '')))
                
                if not self.hash_mod is None:
                    hash_num = int(doc['url_key'][-4:], 16)
                    if hash_num%self.hash_mod[0] != self.hash_mod[1]:
                        continue

                if self.store.check_doc(self.para['base_site_id'], doc['url_key']):
                    self.env['dup_url'] += 1
                    if self.dup_flag > 0:
                        old_doc = self.store.get_doc(self.para['base_site_id'], doc['url_key'])
                        doc['site_para'] = get_value(self.para['site_config'], 'site_para', {})
                        self.env['doc'] = doc
                        self.m_content.run(old_doc)

                else:
                    doc['site_para'] = get_value(self.para['site_config'], 'site_para', {})
                    #self.logger.debug("in task doc %s"%(doc))
                    self.env['doc'] = doc
                    self.m_content.run()
                self.env['total_count'] += 1
                if not self.run_flag:
                    self.logger.debug("%s %s"%(self.site_info, "程序收到停止信号"))
                    self.state_info = '程序收到停止信号,已经成功抓取%d页，处理%d条公告，其中新抓取%d条公告,失败%s条,重复%s条'%(self.env['run_times'], self.env['total_count'], self.env['success_count'], self.env['fail_count'],self.env['dup_url'])
                    return {}
                if self.env['fail_count'] > self.max_allow_fail_count:
                    raise Exception('抓取公告失败次数过多, %d > %d'%(self.env['fail_count'], self.max_allow_fail_count))

            self.state_info = '已经成功抓取%d页，处理%d条公告，其中新抓取%d条公告,失败%s条,重复%s条'%(self.env['run_times'], self.env['total_count'], self.env['success_count'], self.env['fail_count'],self.env['dup_url'])
            self.store.update_task_state({'site_id':self.para['site_id'], 'state_info':self.state_info, 
                    'crawl_para': self.para['crawl_para'],'state':12, 'old_state':12,
            })
            self.logger.debug("%s %s"%(self.site_info, self.state_info))

            #判断是否本次抓取可以停止
            if 'stop_filter' in self.para['site_config']:
                if check_expr_filter(self.para['site_config']['stop_filter'], self.env):
                    break
            if len(self.env['page_result']['next_reqs']) == 0:
                break
            self.env['page_result']['reqs'] = []

        return {}
    
    #任务结束    
    def end(self):
        self.m_content.end()
        self.m_next_page.end()
        self.m_page_list.end()
        self.m_init.end()

        return {}
                        
