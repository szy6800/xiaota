# encoding: UTF-8
from __future__ import division
import json
import sys
import os
import timeit
import time
import configparser
import types
import csv
import logging
import requests
import datetime
import traceback
import hashlib
import copy
import re
from logging.handlers import TimedRotatingFileHandler
import zlib
import psycopg2
import psycopg2.extras
import datetime
from crawl.xt_lib.xt_pub_func import mkdir

#sys.path.append("../xt_lib")
#sys.path.append("../xt_modules")

from xtc_base import *
from crawl.xt_lib.xt_pub_func import *


class XTC_STORE_PG_FILE(BaseStore):
    def init(self, conf, logger):
        self.conf = conf
        self.logger = logger

        self.db_config = {}
        self.db_config['host'] = self.conf.get("store", "host")
        self.db_config['user'] = self.conf.get("store", "user")
        self.db_config['pass'] = self.conf.get("store", "pass")
        self.db_config['name'] = self.conf.get("store", "database")
        self.db_config['port'] = self.conf.getint("store", "port")

        self.db_conn = psycopg2.connect(host = self.db_config['host'], 
            port = self.db_config['port'], user=self.db_config['user'], 
            password=self.db_config['pass'], database=self.db_config['name'])
        self.db_conn.autocommit = True
        self.db_cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        self.data_path = None
        self.data_url = None
        if conf.has_option('store', 'data_path'):
            self.data_path = conf.get('store', 'data_path')
        else:
            self.data_url = conf.get('store', 'data_url')
  
    #保存文件（内容和附件）
    def save_file(self, file_data, year='2022'):
        filename = year + '_' + calc_md5(file_data)
        if not self.data_path is None:
            save_path = os.path.abspath(os.path.join(self.data_path, filename[:4], filename[5:7], filename[7:9]))
            mkdir(save_path)
            save_file = os.path.abspath(os.path.join(save_path, filename))
            fp = open(save_file, 'wb+')
            if type(file_data) == str:
                fp.write(file_data.encode())
            elif type(file_data) == bytes:
                fp.write(file_data)
            else:
                fp.write(str(file_data).encode())
            fp.close()
        else:
            url = self.data_url + '/admin/doc/uploadfile?file_md5=' + filename
            files = {"myfile" : (filename , file_data)}
            res = requests.post(url, files=files)
            if res.json()['code'] < 0:
                raise Exception("save_file fail! " + filename + ' ' + json.dumps(res.json()))
        
        return filename

    #获取文件内容
    def get_file(self, filename):
        data = None
        if not self.data_path is None:
            save_path = os.path.abspath(os.path.join(self.data_path, filename[:4], filename[5:7], filename[7:9], filename))
            fp = open(save_path, 'rb')
            data = fp.read()
            fp.close()
        else:
            url = self.data_url + '/admin/doc/downloadfile?file_md5=' + filename
            res = requests.get(url)
            if res.status_code != 200 or len(res.content) == 0:
                raise Exception("get_file fail! " + filename)
            data = res.content
        return data

    #保存公告
    def save_doc(self, doc, old_doc=None):
        if doc['reqs'][0]['site_id'] == 0:
            return

        m_files = {}
        result = {'contents':[], 'attachments':[]}
        for item in doc['contents']:
            file_md5 = self.save_file(item['data'])
            item['file_md5'] = file_md5
            m_files[file_md5] = 1
            if 'data' in item : del item['data']
            result['contents'].append(item)
        for item in doc['attachments']:
            file_md5 = self.save_file(item['data'])
            item['file_md5'] = file_md5
            m_files[file_md5] = 1
            if 'data' in item : del item['data']
            result['attachments'].append(item)
        req = doc['reqs'][0]
        result['req'] = req
        if 'fails' in doc and len(doc['fails'])>0:
            result['fails'] = doc['fails']
        
        pub_date = get_pub_date(get_value(req, 'pub_date'))
        if old_doc is None:
            sql = "insert into tb_doc(site_id, doc_key, doc_url, para, content_files, state, state_date, sub_id, pub_date) "
            sql+= " values(%s,%s,%s,%s,%s,0,current_timestamp,%s,%s)"
            try:
                self.db_cursor.execute(sql, (req['site_id'], req['url_key'], req['url'],'{}', json.dumps(result),req['sub_id'], pub_date))
            except Exception as ex:
                self.logger.error(traceback.format_exc())
                raise
        else:
            #合并旧doc数据
            for item in old_doc['content_files']['contents']:
                if ('file_md5' in item) and (not item['file_md5'] in m_files):
                    result['contents'].append(item)
                    m_files[item['file_md5']] = 1
            for item in old_doc['content_files']['attachments']:
                if ('file_md5' in item) and (not item['file_md5'] in m_files):
                    result['attachments'].append(item)
                    m_files[item['file_md5']] = 1

            sql = "update tb_doc set doc_url=%s, para=%s, content_files=%s, state=0, state_date=current_timestamp, sub_id=%s, pub_date=%s "
            sql+= " where site_id=%s and doc_id=%s"
            try:
                self.db_cursor.execute(sql, (req['url'],'{}', json.dumps(result),req['sub_id'], pub_date, old_doc['site_id'], old_doc['doc_id']))
            except Exception as ex:
                self.logger.error(traceback.format_exc())
                raise

        return {}

    #写日志
    def insert_crawl_log(self, site_id, level, msg):
        try:
            usql = "insert into tb_crawl_log(site_id, level, msg_time, msg) values(%s,%s,current_timestamp,%s)"
            ret = self.db_cursor.execute(usql, (site_id, level, msg))
        except Exception as ex:
            self.logger.error(traceback.format_exc())
        return {}

    #检查公告是否已经存在
    def check_doc(self, site_id, doc_key):
        sql = "select doc_id from tb_doc where site_id=%s and doc_key=%s"
        try:
            self.db_cursor.execute(sql, (site_id, doc_key))
            rows = self.db_cursor.fetchall()
            if (not rows is None) and len(rows) > 0:
                return True
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            raise

        return False

    #获取公告信息
    def get_doc(self, site_id, doc_key):
        sql = "select * from tb_doc where site_id=%s and doc_key=%s"
        try:
            self.db_cursor.execute(sql, (site_id, doc_key))
            rows = self.db_cursor.fetchall()
            if (not rows is None) and len(rows) > 0:
                return rows[0]
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            raise
        return None

    #获取公告信息
    def get_doc_by_id(self, doc_id):
        sql = "select * from tb_doc where doc_id=%s"
        try:
            self.db_cursor.execute(sql, (doc_id, ))
            rows = self.db_cursor.fetchall()
            if (not rows is None) and len(rows) > 0:
                return rows[0]
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            raise
        return None

    #获取一个待抓取任务
    def get_task(self):
        # sql = "select * from tb_site where state in (10,20) and next_crawl_time < current_timestamp order by site_id limit 1"
        sql = "select * from tb_site where site_id=991"
        try:
            for i in range(100):
                self.db_cursor.execute(sql)
                task = self.db_cursor.fetchone()
                if task is None:
                    #self.logger.debug("get task is None")
                    return None
                ret = self.lock_task(task['site_id'], task['state'])
                self.logger.debug("lock task %s ret=%s"%(task['site_id'], ret))
                if ret == 1:
                    return task
                time.sleep(1)
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            raise
        return None

    def get_task_info(self, site_id):
        sql = "select * from tb_site where site_id=%s"
        try:
            self.db_cursor.execute(sql, (site_id,))
            task = self.db_cursor.fetchone()
            return task
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            raise
        return None

    def lock_task(self, site_id, state, info = ''):
        ret = 0
        try:
            usql = "update tb_site set state=11, state_info=%s where site_id=%s and state=%s"
            self.db_cursor.execute(usql, (info, site_id, state))
            ret = self.db_cursor.rowcount
            #print("run ", usql, ret)
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            raise
        return(ret)

    #更新任务状态
    def update_task_state(self, para):
        if para['site_id'] == 0:
            return
        try:
            #{'site_id':task['site_id'], 'state':12, 'old_state':11, 'info':''}
            v_lsit = []
            usql = "update tb_site set state_date=current_timestamp, state=%s"
            v_lsit.append( para['state'] )
            if para['state'] == 20:
                usql += ",fail_times=0"
            if para['state'] == 19:
                usql += ",fail_times=fail_times+1"
            if 'state_info' in para:
                usql += ",state_info=%s"
                v_lsit.append(f"pid: {os.getpid()} {para['state_info']}")
            if 'next_crawl_time' in para:
                usql += ",next_crawl_time=%s"
                v_lsit.append(para['next_crawl_time'])
            if 'crawl_para' in para:
                usql += ", crawl_para=%s"
                v_lsit.append(json.dumps(para['crawl_para']))

            usql += " where site_id=%s"
            v_lsit.append(para['site_id'])

            if 'old_state' in para:
                usql += " and state=%s"
                v_lsit.append(para['old_state'])
            ret = self.db_cursor.execute(usql, v_lsit)
            if self.db_cursor.rowcount == 0:
                raise Exception('抓取任务状态异常')
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            raise
        return {}

    def get_proxy(self, proxy_key):
        if proxy_key is None:
            return
        times_name = f"get_proxies_times_{proxy_key}"
        if not hasattr(self, 'proxies_md_md'):
            self.proxies_md_md = None
        if not hasattr(self, times_name):
            setattr(self, times_name, 1)
        if getattr(self, times_name) > 10:
            setattr(self, times_name, 1)
        if self.proxies_md_md is not None and getattr(self, times_name) % 10 != 0:
            setattr(self, times_name, getattr(self, times_name) + 1)
            if (datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S") <= \
                    self.proxies_md_md['expire_time']:
                return self.proxies_md_md['proxies']

        sql = "select * from tb_proxy where proxy_key=%s order by id desc limit 1"
        try:
            self.db_cursor.execute(sql, (str(proxy_key),))
            proxy = self.db_cursor.fetchone()
            if (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S") > proxy['state_date'].strftime("%Y-%m-%d %H:%M:%S"):
                proxy = self.update_proxies(proxy_key, proxy)
                self.proxies_md_md = proxy
            else:
                self.proxies_md_md = {"proxies": proxy['proxies'], "expire_time": proxy['state_date'].strftime("%Y-%m-%d %H:%M:%S")}
            return proxy['proxies']
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            raise

    def update_proxies(self, proxy_key, ori_info):
        sql = "SELECT * FROM tb_proxy WHERE id = '1'"
        cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql)
        proxy_ip_info = None
        proxy = cursor.fetchone()
        if proxy :
        # if proxy := cursor.fetchone():
            url = proxy['proxies']['url']
            res = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
            }, verify=False)
            try:
                r_json = res.json()
                d = r_json['data'][0]
                ip = d['ip']
                if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip):
                    proxy_ip_info = {
                        "https": f"https://{d['ip']}:{d['port']}",
                        "http": f"http://{d['ip']}:{d['port']}",
                    }
                else:
                    raise KeyError('ip error')
            except Exception:
                self.logger.error(f"ip 更新失败 id { ori_info['id']} proxy_key {ori_info['proxy_key']}")
            else:
                if proxy_key is not None:
                    sql = 'update tb_proxy set proxies=%s, state_date=%s where id=%s'
                    cursor.execute(sql, [json.dumps(proxy_ip_info), d['expire_time'], ori_info['id']])
                    return {"proxies": proxy_ip_info, 'expire_time': d['expire_time']}
            finally:
                cursor.close()
            return {"proxies": proxy_ip_info, 'expire_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
