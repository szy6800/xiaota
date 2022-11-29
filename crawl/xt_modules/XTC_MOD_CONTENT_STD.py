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

class XTC_MOD_CONTENT_STD(BaseMOD):
    def init(self, task):
        self.task = task
        return {}
    
    def run(self, old_doc = None):
        self.task.logger.debug("%s XTC_MOD_CONTENT_STD doc %s"%(self.task.site_info, self.task.env['doc']))

        self.task.step_info['doc'] = self.task.env['doc']
        self.doc = {'para':self.para,'contents':[], 'attachments':[], 'reqs':[self.task.env['doc']], 'fails':[]}

        if 'req' in self.doc['reqs'][0]:
            self.doc['reqs'].append(self.doc['reqs'][0]['req'])
            del self.doc['reqs'][0]['req']

        if 'reqs' in self.doc['reqs'][0]:
            for req in self.doc['reqs'][0]['reqs']:
                self.doc['reqs'].append(req)
            del self.doc['reqs'][0]['reqs']

        for i in range(100):
            if i >= len(self.doc['reqs']):
                break
            req = self.doc['reqs'][i]

            allow_error_level = get_value(req, 'allow_error_level', 0)
            try:
                res = self.task.request_url(req, self.para)
            except Exception as ex:
                if i == 0 or allow_error_level!=2:
                    raise
                self.doc['fails'].append({'url':get_value(req, 'url', '')})
                continue

            if res.status_code != 200:
                if i > 0 and allow_error_level >= 1:
                    self.doc['fails'].append({'url':res.url})
                    continue

                self.task.env['fail_count'] += 1
                self.task.logger.debug("%s XTC_MOD_CONTENT_STD get fail %s %s"%(self.task.site_info, res.status_code, res.url))
                return {}
            if get_content_type(res, self.task.max_content_size, req) == 'text':
                self.task.logger.debug("%s XTC_MOD_CONTENT_STD add content %s %s"%(self.task.site_info, res.url, get_value(req,'title','')))
                self.doc['contents'].append({'url':str(res.url), 'purl':get_value(req,'purl',''), 'title':get_value(req,'title',''), 'data':res.text})
                self.doc['contents'][-1]['Content-Type'] = get_value(res.headers, 'Content-Type', '')

                if 'check_rules' in self.para:
                    for rule in self.para['check_rules']:
                        cr, msg = check_result_rule(str(res.url), 'content', res.text, rule)
                        if not cr:
                            raise Exception(msg)

                req['text'] = res.text
                req['content'] = res.content
                self.doc['now_req'] = req
                if 'rule' in self.para:
                    pick_data(req, self.para['rule'], self.doc)
                if 'rules' in self.para:
                    for rule in self.para['rules']:
                        pick_data(req, rule, self.doc)
                del req['text']
                del req['content']
                del self.doc['now_req']
            else:
                file_name = get_attachment_file_name(res)
                self.task.logger.debug("%s XTC_MOD_CONTENT_STD add attachment %s %s"%(self.task.site_info, res.url, file_name))

                #if 'check_rules' in self.para:
                #    for rule in self.para['check_rules']:
                #        cr, msg = check_result_rule(str(res.url), 'attachment', res.text, rule)
                #        if not cr:
                #            raise Exception(msg)

                self.doc['attachments'].append({'url':str(res.url), 'purl':get_value(req,'purl',''), 'title':get_value(req,'title',''), 'name':file_name,'data':res.content})
                self.doc['attachments'][-1]['Content-Type'] = get_value(res.headers, 'Content-Type', '')
                
        self.task.logger.debug("%s XTC_MOD_CONTENT_STD save %s fails=%s"%(self.task.site_info, self.task.env['doc'], self.doc['fails']))
        del self.doc['para']

        if old_doc is None and self.task.store.check_doc(self.doc['reqs'][0]['site_id'], self.doc['reqs'][0]['url_key']):
            self.task.env['dup_url'] += 1
            return {}
        self.task.store.save_doc(self.doc, old_doc)
        self.task.env['success_count'] += 1
        return {}
        
    #结束    
    def end(self):
        return {}
                        
