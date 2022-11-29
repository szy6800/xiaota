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
import pymongo
from gridfs import GridFS
from bson.objectid import ObjectId


from .xtc_base import *
from crawl.xt_lib.xt_pub_func import *

class XTC_TASK_MONGO(BaseTask):
    def init(self, logger, store):
        self.logger = logger
        self.store = store
        self.step_info = {}
        self.state_info = ''
        self.site_info = 'site_id=' + str(self.para['site_id']) + ' '
        self.run_flag = True

        mongodb_host = self.store.conf.get("mongodb", "db_host")
        mongodb_port = self.store.conf.getint("mongodb", "db_port")
        mongodb_name = self.store.conf.get("mongodb", "db_name")
        mongodb_user = self.store.conf.get("mongodb", "db_user")
        mongodb_pass = self.store.conf.get("mongodb", "db_pass")

        print(mongodb_host, mongodb_port, mongodb_name, mongodb_user, mongodb_pass)

        if mongodb_user!='':
            self.mongo_conn1 = pymongo.MongoClient(mongodb_host, mongodb_port, username=mongodb_user, password=mongodb_pass, authSource=mongodb_name)
            self.mongo_conn2 = pymongo.MongoClient(mongodb_host, mongodb_port, username=mongodb_user, password=mongodb_pass, authSource=mongodb_name)
        else:
            self.mongo_conn1 = pymongo.MongoClient(mongodb_host, mongodb_port)
            self.mongo_conn2 = pymongo.MongoClient(mongodb_host, mongodb_port)

        self.db_name = get_value(self.para['site_config'], 'db_name', 'Bidding_data')
        self.table_name = get_value(self.para['site_config'], 'table_name', '')
        self.attachment_table_name = get_value(self.para['site_config'], 'attachment_table_name', self.table_name + '_attachment')

        self.db1 = self.mongo_conn1[self.db_name]
        self.db2 = self.mongo_conn2[self.db_name]
        self.gfs = None

        self.logger.debug("%s end in task init modules "%(self.site_info))

        return {}

    def load_gfs_data(self, file_id):
        if self.gfs is None:
            self.gfs = GridFS(self.db2, 'attachment')
        if not self.gfs.exists(file_id):
            return None
        gs_data = self.gfs.get(file_id)
        file_data = gs_data.read()
        return file_data

    def save_doc(self, req, data):
        doc = {'contents':[], 'attachments':[], 'reqs':[req], 'fails':[]}
        content = {'url':req['url'], 'purl':get_value(req,'purl',''), 'title':get_value(req,'title','')}
        if  'original_html' in data and len(data['original_html']) > 0:
            content['data'] = data['original_html']
        else:
            content['data'] = get_value(data, 'body_html', '')
        doc['contents'].append(content)

        for item in self.db2[self.attachment_table_name].find({'_id':data['_id']}):
            if not 'data_list' in item:
                continue
            for file_data in item['data_list']:
                attachment = {}
                attachment['url'] = file_data['file_url']
                attachment['name'] = file_data.get('file_name','')
                attachment['data'] = ''
                if 'file_data' in file_data:
                    attachment['data'] = file_data['file_data']
                elif 'data' in file_data:
                    attachment['data'] = file_data['data']
                if not attachment['data'] is None:
                    if type(attachment['data']) == ObjectId:
                        attachment['data'] = self.load_gfs_data(attachment['data'])
                        
                    #对附件的data不是str, bytes的情况， 先不保存此公告
                    if not type(attachment['data']) in (str, bytes):
                        self.env['fail_count'] += 1
                        return {}
                    doc['attachments'].append(attachment)

        self.store.save_doc(doc)
        self.env['success_count'] += 1
        return {}

    def run(self):
        self.logger.debug("%s in task run"%(self.site_info))

        self.env['dup_url'] = 0
        self.env['run_times'] = 0
        self.env['fail_count'] = 0
        self.env['success_count'] = 0
        self.env['total_count'] = 0

        self.start_date = '2021-01-01'
        self.end_date = '2022-07-01'

        while self.run_flag:
            self.env['run_times'] += 1

            self.step_info = {}
            for data in self.db1[self.table_name].find().sort([('_id', pymongo.DESCENDING)]):
                self.env['total_count'] += 1
                if not self.run_flag:
                    self.logger.debug("%s %s"%(self.site_info, "程序收到停止信号"))
                    self.state_info = '程序收到停止信号,已经成功抓取%d页，处理%d条公告，其中新抓取%d条公告,失败%s条,重复%s条'%(self.env['run_times'], self.env['total_count'], self.env['success_count'], self.env['fail_count'],self.env['dup_url'])
                    return {}

                self.state_info = '已经成功抓取%d页，处理%d条公告，其中新抓取%d条公告,失败%s条,重复%s条'%(self.env['run_times'], self.env['total_count'], self.env['success_count'], self.env['fail_count'],self.env['dup_url'])
                if self.env['total_count'] % 1000 == 1:
                    self.store.update_task_state({'site_id':self.para['site_id'], 'state_info':self.state_info, 
                            'crawl_para': self.para['crawl_para'],'state':12, 'old_state':12,
                    })
                    self.logger.debug("%s %s"%(self.site_info, self.state_info))

                req = {}
                #['_id', 'ref_url', 'title', 'publish_time', 'anoucement_type', 'province', 'city', 'abstract_html', 'buyer_name', 'bid_winning_amount', 'source', 'project_name', 'body_html', 'original_html', 'tags', 'attachment_flag']
                for key in data.keys():
                    if key in ['_id', 'body_html', 'original_html', 'abstract_html','tags', 'attachment_flag']:
                        continue
                    elif key == 'publish_time':
                        req['pub_date'] = data[key]
                    elif key == 'ref_url':
                        req['url'] = data[key]
                    elif key == 'ref_url':
                        req['url'] = data[key]
                    elif key == 'anoucement_type':
                        req['stage'] = data[key]
                    else:
                        req[key] = data[key]
                
                if (not 'url' in req) or (not 'pub_date' in req):
                    self.env['fail_count'] += 1
                    continue

                if req['pub_date'] < self.start_date or req['pub_date'] > self.end_date:
                    self.env['dup_url'] += 1
                    continue

                req['site_id'] = self.para['base_site_id']
                req['sub_id'] = self.para['site_id']
                if 'url_key_expr' in self.para['site_config']:
                    req['url_key'] = calc_md5(eval(self.para['site_config']['url_key_expr'], None, req))
                else:
                    req['url_key'] = calc_md5(get_full_url(req['url'], get_value(req, 'purl', '')))
                
                if self.store.check_doc(self.para['base_site_id'], req['url_key']):
                    self.env['dup_url'] += 1
                else:
                    req['site_para'] = get_value(self.para['site_config'], 'site_para', {})
                    self.save_doc(req, data)

                #判断是否本次抓取可以停止
                if 'stop_filter' in self.para['site_config']:
                    if check_expr_filter(self.para['site_config']['stop_filter'], self.env):
                        break
            break
        return {}
    
    #任务结束    
    def end(self):
        self.mongo_conn1.close()
        self.mongo_conn2.close()
        return {}
                        
