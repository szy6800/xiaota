# encoding: UTF-8
from __future__ import division
import datetime
from cgitb import html
from email import header
import os
import sys
import time
import logging
import traceback
import urllib
import json
import threading
import copy
import hashlib
import base64
import math
import re
from bs4 import BeautifulSoup
import bs4
import lxml
from lxml import etree
import requests
import httpx
#import demjson
from dateutil import parser as date_string_parser
#from splash_help import SplashHelp

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5 as PKCS1_cipher
from dateutil import parser


from xt_lib.xt_pub_func import *

###########这个脚本是给大家进行交互测试的，适合贴到交互工具上逐块执行的
##########日常逐条请求###########
#这个是我们task模块中的缺省headers
base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
            'Upgrade-Insecure-Requests': '1'
        }

#这里我们先建立一个session， 后面的请求都要用ss发起
ss = requests.session()
#如果是http2， 就用下面这个
#ss = httpx.Client(http2=True)

#############################################################
######开始请求链接了
headers = base_headers.copy()

url = 'https://fzsggzyjyfwzx.cn/jyxxzfcg/index.jhtml'
res = ss.get(url, headers=headers)

#请求完成后， 查看res.text, 确定是否要修改编码
res.encoding = 'utf8'

#############################################################
#测试soup功能, 或者xpaht等等
soup = BeautifulSoup(res.text, 'lxml')
m_list = soup.select(".article-list3-t")
print(len(m_list))
print(m_list[0])


#############################################################
#测试pick规则的准确性
#构造req, 和配置中一样（或者是和你生成的doc一样）
req = {
    "url": "https://fzsggzyjyfwzx.cn/jyxxzfcg/index.jhtml"
}
#给req补充来着请求结果第信息
req['text'] = res.text
req['content'] = res.content #这个可以不提供，目前没有使用

#当然也可以直接用用你的文本填充req['text']
#req['text'] = 'test text'

page_result = {}
#如果规则中还用到了其它信息， 这里补充到page_result中 
page_result['now_req'] = req

#构造pick规则
rule = {
        "pick": {
          "type": "soup",
          "pattern": ".article-list3-t",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "docs.+.url",
                "expr": "values['soup'].a['href']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.purl",
                "expr": "obj['now_req']['url']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.title",
                "expr": "values['soup'].a.text.strip()"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "values['soup'].div.text.strip()"
              }
            ]
          }
        }
      }

pick_data(req, rule, page_result)

#准备查看pick规则执行第结果， 先删除text,content是为了让结果容易看
del req['text']
del req['content']
print(json.dumps( page_result, indent=2, ensure_ascii=False))