# encoding: UTF-8
from __future__ import division
import json
import sys
import os
import timeit
import time
import types
import csv
import logging
import datetime
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib
import urllib.parse

def default_callback_func(paras, handle):
    print('default_callback_func', paras)
    return {'code':0, 'msg':'success'}

class JsonServerHandler(BaseHTTPRequestHandler):
    def send_result(self, result):
        self.protocal_version = 'HTTP/1.1' 
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(result)
        
    def _deal(self, paras):
        #print("in deal paras=%s"%(paras))
        try:
            result = default_callback_func(paras, self)
        except Exception as err:
            print(traceback.format_exc())
            result = {"code":-100, "msg": str(traceback.format_exc())}
        #print("result=%s"%(result))
        self.send_result(bytes( json.dumps(result),  encoding = "utf8"))
        
    def do_POST(self):
        #logging.warning(self.path)
        query = urllib.parse.splitquery(self.path)
        #print(query)
        params = {}
        if query[1] != '':
            params=urllib.parse.parse_qs(query[1])
        #print("post ", params)
        paras = {}
        for key, item in params.items():
            paras[key] = item[0]
        
        length = int(self.headers['content-length'])
        content = self.rfile.read(length)
        content = str(content, encoding = "utf-8")
        #print(content)
        if content != '' :
            params=urllib.parse.parse_qs(content)
        #print("post content ", params)
        for key, item in params.items():
            paras[key] = item[0]
        
        self._deal(paras)
        
    def do_GET(self):
        query = urllib.parse.splitquery(self.path)
        params = {}
        if query!=None and query[1] != '':
            params=urllib.parse.parse_qs(query[1])
        #print("get ", params)
        paras = {}
        for key, item in params.items():
            paras[key] = item[0]
        self._deal(paras)
        
    def log_request(self, code='-', size='-'):
        pass
