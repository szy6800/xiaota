# encoding: UTF-8
from __future__ import division
import os
import sys
import time
import datetime
import logging
import traceback
import urllib
import json
import threading
import copy

from xtc_base import *
from crawl.xt_lib.xt_pub_func import *

class XTC_FRAME_STD(BaseFrame):
    def init(self):
        self.m_task = None
        log_name = self.conf.get('log', 'module_name')
        self.logger = LoadXTClass(log_name)({})
        self.logger.init(self.conf)

        self.logger.debug("begin init store")

        store_name = self.conf.get('store', 'module_name')
        self.store = LoadXTClass(store_name)({})
        self.store.init(self.conf, self.logger)

        return {}
    
    def run(self):
        run_times = 0 
        deal_times = 0
        while self.run_flag:
            run_times += 1
            if run_times > 300 or deal_times > 1:
                self.logger.debug("exit for %s %s"%(run_times, deal_times))
                return {}

            try:
                task = None
                self.logger.task = None
                task = self.store.get_task()
                if task is None:
                    #self.logger.debug("get task empty")
                    time.sleep(2)
                    continue
                self.run_flag = False
                deal_times += 1
                self.logger.debug("begin deal task site_id=%s"%(task['site_id']))
                self.store.update_task_state({'site_id':task['site_id'], 'state':12, 'old_state':11, 'state_info':''})

                if task['base_site_id'] != 0 and get_value(task['site_config'], 'load_from_parent', False):
                    base_task = self.store.get_task_info(task['base_site_id'])
                    merge_config(base_task['site_config'], task['site_config'])
                    task['site_config'] = base_task['site_config']
                    task['site_script'] = base_task['site_script']

                if task['base_site_id'] == 0:
                    task['base_site_id'] = task['site_id']

                #print(json.dumps(task['site_config'], indent=2, ensure_ascii=False))

                self.logger.debug("init task site_id=%s %s"%(task['site_id'], task['site_config']['task_module']))
                self.m_task = LoadXTClass(task['site_config']['task_module'])(task)
                self.m_task.frame = self
            
                self.logger.debug("call task init site_id=%s"%(task['site_id']))
                self.m_task.init(self.logger, self.store)

                self.logger.debug("call task run site_id= %s"%(task['site_id']))
                if "write_db_log" in task['site_config']:
                    self.logger.task = self.m_task
                self.m_task.run()

                self.logger.debug("call task end site_id=%s"%(task['site_id']))
                self.m_task.end()
                self.store.update_task_state({'site_id':task['site_id'], 'state':20, 'old_state':12, 'state_info':self.m_task.state_info, 
                    'next_crawl_time':(datetime.datetime.now() + datetime.timedelta(seconds=task['crawl_interval'])).strftime('%Y-%m-%d %H:%M:%S'),
                    'crawl_para': self.m_task.para['crawl_para']
                })
                self.logger.debug("end deal task site_id=%s"%(task['site_id']))
                self.m_task = None
            except Exception as ex:
                if not task is None:
                    self.logger.error('site_id=%s %s'%(task['site_id'], traceback.format_exc()))
                else:
                    self.logger.error(traceback.format_exc())
                if not task is None:
                    step_info = ''
                    try:
                        if not self.m_task is None:
                            step_info += json.dumps(self.m_task.step_info, ensure_ascii=False)
                    except:
                        pass
                    self.store.update_task_state({'site_id':task['site_id'], 'state':19, 'state_info':step_info + '\n' + traceback.format_exc()})
                time.sleep(10)
        return {}

    def test(self, task):
        try:
            if get_value(task, 'base_site_id', 0) == 0:
                 task['base_site_id'] = task['site_id']

            self.m_task = LoadXTClass(task['site_config']['task_module'])(task)
            self.m_task.frame = self
        
            self.logger.debug("call task init %s"%(task['site_id']))
            self.m_task.init(self.logger, self.store)

            self.logger.debug("call task run %s"%(task['site_id']))
            self.m_task.run()

            self.logger.debug("call task end %s"%(task['site_id']))
            self.m_task.end()
            self.store.update_task_state({'site_id':task['site_id'], 'state':20, 'old_state':12, 'state_info':self.m_task.state_info, 
                'next_crawl_time':(datetime.datetime.now() + datetime.timedelta(seconds=task['crawl_interval'])).strftime('%Y-%m-%d %H:%M:%S'),
                'crawl_para': self.m_task.para['crawl_para']
            })
            self.logger.debug("end deal task %s"%(task['site_id']))
            self.m_task = None
        except Exception as ex:
            self.logger.error(traceback.format_exc())
        return {}

    #结束    
    def end(self):
        return {}

