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
import psycopg2
import psycopg2.extras


from .xtc_base import *
from crawl.xt_lib.xt_pub_func import *


class XTC_TASK_LOAD_DOC(BaseTask):
    def init(self, logger, store):
        self.logger = logger
        self.store = store
        self.step_info = {}
        self.state_info = ''
        self.site_info = 'site_id=' + str(self.para['site_id']) + ' '
        self.run_flag = True

        self.mongo_conn = pymongo.MongoClient('192.168.1.201', 27018)
        self.mongo_db = None
        self.mongo_gfs = None

        self.db_conn = psycopg2.connect(host='192.168.1.201', port=5432, user='postgres', password='123456', database='datacheck')
        self.db_conn.autocommit = True
        self.db_cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        self.logger.debug("%s end in task init modules "%(self.site_info))

        return {}

    def load_gfs_data(self, file_id):
        if self.mongo_gfs is None:
            self.mongo_gfs = GridFS(self.mongo_db, 'attachment')
        if not self.mongo_gfs.exists(file_id):
            return None
        gs_data = self.mongo_gfs.get(file_id)
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

        for item in self.mongo_db[self.attachment_table_name].find({'_id':data['_id']}):
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

    def save_announcement(self, req, announcement):
        result = {'win_infos':[], 'products':[], 'announcement_id':str(announcement['id'])}
        #announcement
        if not announcement['project_no'] is None:
            result['project_no'] = announcement['project_no']
        if not announcement['title'] is None:
            result['title'] = announcement['title']
        if not announcement['project_name'] is None:
            result['project_name'] = announcement['project_name']

        if not announcement['publish_time'] is None:
            result['publish_date'] = str(announcement['publish_time'])
        if not announcement['tender_date'] is None:
            result['tender_date'] = str(announcement['tender_date'])
        if not announcement['winning_date'] is None:
            result['winning_date'] = str(announcement['winning_date'])
        if not announcement['total_bid_amount'] is None:
            result['total_bid_amount'] = str(announcement['total_bid_amount'])

        purchase_info = {}
        if not announcement['purchaser'] is None:
            purchase_info['name'] = announcement['purchaser']
        if not announcement['project_user'] is None:
            purchase_info['contact_person'] = announcement['project_user']
        if not announcement['project_mobile'] is None:
            purchase_info['mobile'] = announcement['project_mobile']
        if not announcement['purchase_address'] is None:
            purchase_info['address'] = announcement['purchase_address']
        if not announcement['purchase_mobile'] is None:
            purchase_info['mobile'] = announcement['purchase_mobile']
        if not announcement['project_user_address'] is None:
            purchase_info['address'] = announcement['project_user_address']
        if not announcement['purchase_user'] is None:
            purchase_info['contact_person'] = announcement['purchase_user']
        if len(purchase_info) > 0:
            result['purchase_info'] = purchase_info

        agency_info = {}
        if not announcement['agency_name'] is None:
            agency_info['name'] = announcement['agency_name']
        if not announcement['agency_address'] is None:
            agency_info['address'] = announcement['agency_address']
        if not announcement['agency_mobile'] is None:
            agency_info['mobile'] = announcement['agency_mobile']
        if not announcement['agency_user'] is None:
            agency_info['contact_person'] = announcement['agency_user']
        if len(agency_info) > 0:
            result['agency_info'] = agency_info

        review_expert = {}
        if not announcement['review_expert'] is None:
            review_expert['name'] = announcement['review_expert']
        if len(review_expert) > 0:
            result['review_expert'] = review_expert

        area = {}
        if not announcement['province'] is None:
            area['province'] = announcement['province']  #需要转换
        if not announcement['review_expert'] is None:
            area['city'] = announcement['city']
        if not announcement['county'] is None:
            area['district'] = announcement['county']
        if len(area) > 0:
            result['area'] = area

        #bid_company
        sql = 'select * from stage_win_bid_company_3 where announcement_id=%s'
        res = self.db_cursor.execute(sql, (announcement['id'],))
        datas = self.db_cursor.fetchall()
        for data in datas:
            item = {}
            if not data['company_name'] is None:
                item['name'] = data['company_name']
            if not data['company_winning_amount'] is None:
                item['win_amount'] = str(data['company_winning_amount'])
            if not data['package'] is None:
                item['package'] = str(data['package'])
            if not data['winning_user'] is None:
                item['contact_person'] = data['winning_user']
            if not data['winning_address'] is None:
                item['address'] = data['winning_address']
            if not data['winning_mobile'] is None:
                item['mobile'] = data['winning_mobile']
            result['win_infos'].append(item)

        #bid_target
        sql = 'select * from stage_win_bid_target_3 where announcement_id=%s'
        res = self.db_cursor.execute(sql, (announcement['id'],))
        datas = self.db_cursor.fetchall()
        for data in datas:
            item = {}
            if not data['package'] is None:
                item['package'] = str(data['package'])
            if not data['product_model_name'] is None:
                item['type'] = data['product_model_name']
            if not data['product_name'] is None:
                item['name'] = data['product_name']
            if not data['company_name'] is None:
                item['company'] = data['company_name']

            if not data['unit_price'] is None:
                item['price'] = str(data['unit_price'])
            if not data['unit_amount'] is None:
                item['num'] = str(data['unit_amount'])
            if not data['total_price'] is None:
                item['total_amount'] = str(data['total_price'])
            result['products'].append(item)

        req['result'] = result

        self.mongo_db = self.mongo_conn[announcement['source'][0]['data_base']]
        data = self.mongo_db[announcement['source'][0]['collection']].find_one({'_id':ObjectId(announcement['source'][0]['mongo_id'])})
        self.attachment_table_name = announcement['source'][0]['collection'] + '_attachment'

        if data is None:
            self.logger.debug("%s load mongo fail id=%s req=%s mongo_id=%s"%(self.site_info, announcement['id'], req, announcement['source'][0]['mongo_id']))
            self.env['fail_count'] += 1
            return {}

        #['_id', 'ref_url', 'title', 'publish_time', 'anoucement_type', 'province', 'city', 'abstract_html', 'buyer_name', 'bid_winning_amount', 'source', 'project_name', 'body_html', 'original_html', 'tags', 'attachment_flag']
        for key in data.keys():
            if key not in ['publish_time', 'ref_url', 'anoucement_type', 'project_id','title', 'province', 'city', 'project_name', '']:
                continue
            if key == 'publish_time':
                req['pub_date'] = data[key]
            elif key == 'ref_url':
                req['url'] = data[key]
            elif key == 'anoucement_type':
                req['stage'] = data[key]
            else:
               req[key] = data[key]

        self.save_doc(req, data)
        return {}

    def load_announcements(self):
        sql = "select * from stage_win_bid_announcement_3 where publish_time >= '2021-01-01' order by id"
        #sql+= ' limit 2'
        res = self.db_cursor.execute(sql)
        datas = self.db_cursor.fetchall()
        if datas is None:
            return []
        return datas

    def run(self):
        self.logger.debug("%s in task run"%(self.site_info))

        self.env['dup_url'] = 0
        self.env['run_times'] = 0
        self.env['fail_count'] = 0
        self.env['success_count'] = 0
        self.env['total_count'] = 0

        while self.run_flag:
            self.env['run_times'] += 1

            self.step_info = {}
            announcements = self.load_announcements()
            for announcement in announcements:
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
                if not announcement['source'] is None and len(announcement['source']) > 0:
                    req['url'] = announcement['source'][0]['ref_url']

                
                if (not 'url' in req) or (not 'mongo_id' in announcement['source'][0]):
                    self.env['fail_count'] += 1
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
                    self.logger.debug("%s begin %s req=%s"%(self.site_info, announcement['id'], req))
                    req['site_para'] = get_value(self.para['site_config'], 'site_para', {})
                    try:
                        self.save_announcement(req, announcement)
                    except Exception as ex:
                        self.logger.debug("%s fail %s %s"%(self.site_info, announcement['id'], traceback.format_exc()))
                        self.env['fail_count'] += 1

                #判断是否本次抓取可以停止
                if 'stop_filter' in self.para['site_config']:
                    if check_expr_filter(self.para['site_config']['stop_filter'], self.env):
                        break
            self.state_info = '已经成功抓取%d页，处理%d条公告，其中新抓取%d条公告,失败%s条,重复%s条'%(self.env['run_times'], self.env['total_count'], self.env['success_count'], self.env['fail_count'],self.env['dup_url'])
            self.logger.debug("%s end %s"%(self.site_info, self.state_info))
            break
        return {}
    
    #任务结束    
    def end(self):
        self.mongo_conn.close()
        self.db_conn.close()
        return {}
                        
