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


#sys.path.append("../xt_lib")

def LoadXTModule(module_name, need_reload = False):
    global g_modules
    if not 'g_modules' in globals():
        g_modules = {}
    if module_name in g_modules:
        md = g_modules[module_name]['md']
        return(md)
    md = __import__(module_name)
    lt = time.time()
    g_modules[module_name] = {'md':md, 'ft':0, 'lt':lt}
    return(md)

def LoadXTClass(module_name, class_name = '', need_reload = False):
    if class_name == '':
        class_name = module_name    
    print("load module=%s class=%s"%(module_name, class_name))
    md = LoadXTModule(module_name, need_reload)
    cls = getattr(md, class_name)
    return cls

def InitModuleFromPara(para, para_key, base_module_class, need_reload = False):
    if para_key == '':
        mpara = para
    else:
        if not para_key in para:
            return base_module_class({})
        mpara = para[para_key]
    cls = LoadXTClass(mpara['module_name'], need_reload=need_reload)
    return cls(mpara['module_para'])


########################################################

#日志记录基类
class BaseLog(object):
    def __init__(self, para):
        self.para = para
        self.level = 0
        
    def init(self, conf):
        pass
    
    def debug(self, info):
        self.log(0, info)

    def info(self, info):
        self.log(1, info)

    def warning(self, info):
        self.log(2, info)

    def error(self, info):
        self.log(3, info)

    def log(self, level, info):
        print(info)

#存储基类
class BaseStore(object):
    def __init__(self, para):
        self.para = para
        
    def init(self, conf, logger):
        self.logger = logger
        pass
    
    #保存文件（内容和附件）
    def save_file(self, file_data):
        return {}

    #获取文件内容
    def get_file(self, file_key):
        return None

    #保存公告
    def save_doc(self, doc):
        return {}
    
    #检查公告是否已经存在
    def check_doc(self, site_id, doc_key):
        return False

    #获取公告信息
    def get_doc(self, site_id, doc_key):
        return {}

    #获取一个待抓取任务
    def get_task(self):
        return None

    #更新任务状态
    def update_task_state(self, para):
        return {}

    



#模块基类
class BaseMOD(object):
    def __init__(self, para):
        self.para = para
        
    def init(self, task):
        return {}
    
    def run(self):
        return {}
        
    #结束    
    def end(self):
        return {}

#业务主框架基类
class BaseFrame(object):
    def __init__(self, conf):
        self.conf = conf
        
    def init(self):
        return {}
    
    def run(self):
        return {}
        
    #结束    
    def end(self):
        return {}




#任务类基类
class BaseTask(object):
    def __init__(self, para):
        self.para = para
        self.env = {}
        self.state = 0
        
    def init(self, logger, store):
        self.logger = logger
        self.store = store
        
        return {}
        
    def run(self):
        return {}
    
    #任务结束    
    def end(self):
        return {}




########################################################################

def init_g_modules():
    global g_modules
    if not 'g_modules' in globals():
        g_modules = {}
    return g_modules

