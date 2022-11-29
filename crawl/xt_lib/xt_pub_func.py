# encoding: UTF-8
from __future__ import division
import datetime
from cgitb import html
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
import demjson
from dateutil import parser as date_string_parser
from splash_help import SplashHelp
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5 as PKCS1_cipher
from Cryptodome.Cipher import AES, DES
from dateutil import parser
import ddddocr

class TimeCheckError(Exception):

    def __init__(self, *args):

        super(TimeCheckError, self).__init__(*args)


def exec_string(function_string: str, function_name='eval_string', **kwargs):
    """
        执行配制中的函数
        example:
            def example():print(1);abcd_2();return "我是返回执"\ndef abcd_2():print(3)
            print(exec_callback(example_string, "abcd", ))
            或  (注意格式)
            def abcd():
            try:
                print(1)
            except:
                print(2)

            两个函数间用 \n 相隔
            class A:
                def __init__(self, a=xx, *args, **kwargs):pass
                def run():
                    print(1)

            def run():
                a = A(*args, **kwargs)
                return a.run()
             print(exec_callback(example_string, "run", *args, **kwargs))
        :param function_string: 函数字符串
        :param function_name: 函数名 启动函数
        :param kwargs: 函数的 kw 参数
        :return:
        """
    namespace = {"json": json, "urllib": urllib, "base64": base64, "hashlib": hashlib, "math": math, "etree": etree,
                 "BeautifulSoup": BeautifulSoup, "requests": requests, "lxml": lxml,
                 'demjson': demjson, 
                 'sys': sys, 'time': time, "SplashHelp": SplashHelp}
    function_string = _strip(function_string)
    fun = compile(function_string, '<string>', 'exec')
    exec(fun, namespace)
    result = namespace[function_name](**kwargs)
    return result


def _strip(function_string):
    """
    整体对空格做相同处理
    @param function_string:
    @return:
    """
    s_list = function_string.split('\n')
    result_str = ''
    first = True
    count = 0
    for s in s_list:
        if s and s != '\n':
            if first:
                first = False
                for _ in s:
                    if _ == ' ':
                        count += 1
                    else:
                        break
                result_str += s.strip() + "\n"
            else:
                result_str += s[count:] + "\n"

    return result_str


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def strToJson(str):
    try:
        result = json.loads(str)
        return result
    except:
        return {}


def calc_md5(data, coding='utf8'):
    if type(data) == str:
        temp = data.encode(coding)
    elif type(data) == bytes:
        temp = data
    else:
        temp = str(data).encode(coding)
    return hashlib.md5(temp).hexdigest()


def make_base64(data, coding='utf8'):
    if type(data) == str:
        temp = data.encode(coding)
    else:
        temp = data
    return base64.encodebytes(temp).decode(coding)


def parse_base64(data, coding='utf8'):
    if type(data) == str:
        temp = data.encode(coding)
    else:
        temp = data
    return base64.decodebytes(temp).decode(coding)

def rsa_encrypt(pkey, data, length=50):
    key = '-----BEGIN PUBLIC KEY-----\n' + pkey + '\n-----END PUBLIC KEY-----'
    pub_key = RSA.importKey(str(key))
    cipher = PKCS1_cipher.new(pub_key)
    data = data.encode()
    if len(data) <= length:
        result = base64.b64encode(cipher.encrypt(data))
    else:
        rsa_text = b""
        for i in range(0, len(data), length):
            cont = data[i:i + length]
            rsa_text += cipher.encrypt(cont)

        result = base64.b64encode(bytes.fromhex(rsa_text.hex()))
    return result.decode()

def get_full_url(url, base_url):
    if url[:7].lower() == 'http://' or url[:8].lower() == 'https://':
        return url
    return urllib.parse.urljoin(base_url, url)


def get_html_charset(text):
    try:
        mr = re.search('<meta .*(http-equiv="?Content-Type"?.*)?charset="?([a-zA-Z0-9_-]+)"?', text, re.I)
        if mr:
            charset = mr.group(2).lower()
            return charset
    except:
        pass
    return ''


def get_content_type(res, max_content_size = 2000000, req = None):
    if not req is None:
        ctype = get_value(req, "ctype", "")
        if ctype == 'json':
            return 'text'
        if ctype == 'data':
            return ''
    if 'Content-Disposition' in res.headers:
        return ''
    if len(res.content) > max_content_size:
        return ''

    if 'Content-Type' in res.headers:
        if res.headers['Content-Type'].find('text') >= 0:
            return 'text'
        if res.headers['Content-Type'].find('html') >= 0:
            return 'text'
        if res.headers['Content-Type'].find('json') >= 0:
            return 'text'
    return ''


def get_attachment_file_name(res):
    file_name = ''
    if 'Content-Disposition' in res.headers:
        file_name = urllib.parse.unquote(res.headers['Content-Disposition'].split('filename=')[-1].split(';')[0])
        try:
            file_name = file_name.encode('ISO-8859-1').decode('utf8')
        except:
            try:
                file_name = file_name.encode('ISO-8859-1').decode('gbk')
            except:
                pass
        file_name = file_name.strip('" ').strip()
    return file_name


##############################################
def set_key_values(obj, values, key, expr):
    try:
        keys = key.split('.')
        if len(keys) == 0 or keys[0] == '+':
            return

        for i in range(len(keys)):
            keys[i] = keys[i].replace('$$DOT$$', '.')

        m_var = obj
        for i in range(len(keys)):
            if keys[i] is None or keys[i] == '':
                return

            if i == len(keys) - 1:
                if keys[i] == '+':
                    m_var.append(eval(expr))
                elif keys[i].isdigit() or (keys[i][0] == '-' and keys[i][1:].isdigit()):
                    if "def eval_string" in expr:
                        m_var[int(keys[i])] = exec_string(expr, obj=obj, values=values)
                    else:
                        m_var[int(keys[i])] = eval(expr)
                    if isinstance(m_var[keys[i]], str):
                        m_var[keys[i]] = m_var[keys[i]].strip()
                    if keys[i] == "pub_date":
                        m_var[keys[i]] = check_time(m_var[keys[i]])
                else:
                    if "def eval_string" in expr:
                        m_var[keys[i]] = exec_string(expr, obj=obj, values=values)
                    else:
                        m_var[keys[i]] = eval(expr)
                    if isinstance(m_var[keys[i]], str):
                        m_var[keys[i]] = m_var[keys[i]].strip()
                    if keys[i] == "pub_date":
                        m_var[keys[i]] = check_time(m_var[keys[i]])

            else:
                if keys[i] == '+':
                    if keys[i + 1] == '+':
                        m_var.append([])
                    else:
                        m_var.append({})
                    m_var = m_var[-1]
                elif keys[i].isdigit() or (keys[i][0] == '-' and keys[i][1:].isdigit()):
                    m_var = m_var[int(keys[i])]
                elif keys[i] in m_var:
                    m_var = m_var[keys[i]]
                else:
                    if keys[i + 1] == '+':
                        m_var[keys[i]] = []
                    else:
                        m_var[keys[i]] = {}
                    m_var = m_var[keys[i]]
    except TimeCheckError as e:
        raise e
    except Exception:
        traceback.print_exc()


def get_value(data, key, default=None):
    if data is None or (not key in data):
        return default
    return data[key]


def simple_set_key_value(data, key, value):
    data[key] = value


def check_filter(text, filter):
    if filter is None or filter == '':
        return True
    if text is None or text == '':
        return False
    if re.search(filter, text, re.M | re.I):
        return True
    return False


def check_expr_filter(expr, data):
    return eval(expr, None, data)


def pick_data(data, rule, result):
    if 'url' in data:
        if not check_filter(data['url'], get_value(rule, 'url_filter', '')):
            return
        if 'not_url_filter' in rule:
            if check_filter(data['url'], get_value(rule, 'not_url_filter', '')):
                return

    if not check_filter(data['text'], get_value(rule, 'filter', '')):
        return

    if 'not_filter' in rule:
        print("not_filter", data['text'], get_value(rule, 'not_filter', ''))
        if check_filter(data['text'], get_value(rule, 'not_filter', '')):
            return

    pick = get_value(rule, 'pick', None)
    picks = get_value(rule, 'picks', [])
    if not pick is None:
        picks.insert(0, pick)

    action = get_value(rule, 'action', None)
    actions = get_value(rule, 'actions', [])
    if not action is None:
        actions.insert(0, action)

    if 'action_filter' in rule:
        if not check_expr_filter(rule['action_filter'], {'values':data}):
            actions = []

    for action in actions:
        if check_filter(data['text'], get_value(action, 'filter', '')):
            if action['type'] == 'set_value':
                set_key_values(result, data, action['key'], action['expr'])

    for pick in picks:
        if check_filter(data['text'], get_value(pick, 'filter', '')):
            if pick['type'] == 'soup':
                if 'soup' in data:
                    soup = data['soup']
                else:
                    soup = BeautifulSoup(data['text'], 'lxml')
                items = soup.select(pick['pattern'])
                if 'sub' in pick:
                    for item in items:
                        pick_data({'type': 'soup', 'soup': item, 'text': str(item)}, pick['sub'], result)
            elif pick['type'] == 're':
                re_index = get_value(pick, 're_index', 0)
                re_flag = get_value(pick, 're_flag', 0)
                items = re.findall(pick['pattern'], data['text'], re.M | re.I | re_flag)
                if 'sub' in pick:
                    for item in items:
                        if item == '':
                            continue
                        pick_data({'type': 'reg', 'values': item, 'text': item[re_index]}, pick['sub'], result)
            elif pick['type'] == 'json':
                if 'jdata' in data:
                    jdata = data['jdata']
                else:
                    jdata = json.loads(data['text'], strict=False)
                items = eval(pick['pattern'])
                if not type(items) == list:
                    items = [items]
                if 'sub' in pick:
                    for item in items:
                        if type(item) == list or type(item) == dict:
                            pick_data({'type': 'json', 'jdata': item, 'text': json.dumps(item)}, pick['sub'], result)
                        else:
                            pick_data({'type': 'json', 'jdata': item, 'text': str(item)}, pick['sub'], result)
            elif pick['type'] == 'xpath':
                if 'xdata' in data:
                    xdata = data['xdata']
                else:
                    xdata = etree.HTML(data['text'])
                items = xdata.xpath(pick['pattern'])
                if 'sub' in pick:
                    for item in items:
                        pick_data({'type': 'xpath', 'xdata': item, 'text': etree.tostring(item).decode('utf8')},
                                  pick['sub'], result)
            elif pick['type'] == 'expr':
                items = eval(pick['pattern'], None, data)
                if type(items) == str:
                    items = [items]
                if 'sub' in pick:
                    for item in items:
                        pick_data({'type': 'expr', 'text': item}, pick['sub'], result)


# 返回True表示页面合格
def check_result_rule(url, content_type, data, rule):
    print("check_result_rule", rule, content_type, url, data)
    if 'type_filter' in rule:
        if rule['type_filter'] != content_type:
            return True, ''
    if not check_filter(url, get_value(rule, 'url_filter', '')):
        return True, ''
    if 'not_url_filter' in rule:
        if check_filter(url, get_value(rule, 'not_url_filter', '')):
            return True, ''

    if 'error_reg' in rule and len(rule['error_reg']) > 0:
        result = True
        for e_reg in rule['error_reg']:
            if not check_filter(data, e_reg):
                result = False
                break
        if result:
            return False, 'error_reg=%s' % (rule['error_reg'])

    if 'succ_reg' in rule and len(rule['succ_reg']) > 0:
        result = True
        for e_reg in rule['succ_reg']:
            if not check_filter(data, e_reg):
                result = False
                break
        if not result:
            return False, 'succ_reg=%s' % (rule['succ_reg'])

    if 'error_soup' in rule and len(rule['error_soup']) > 0:
        soup = BeautifulSoup(data, 'lxml')
        result = True
        for e_reg in rule['error_soup']:
            items = soup.select(e_reg)
            if not len(items) > 0:
                result = False
                break
        if result:
            return False, 'error_soup=%s' % (rule['error_soup'])

    if 'succ_soup' in rule and len(rule['succ_soup']) > 0:
        soup = BeautifulSoup(data, 'lxml')
        result = True
        for e_reg in rule['succ_soup']:
            items = soup.select(e_reg)
            if len(items) > 0:
                result = False
                break
        if not result:
            return False, 'succ_soup=%s' % (rule['succ_soup'])

    if 'min_size' in rule:
        if len(data) < rule['min_size']:
            return False, 'size=%s < %s' % (len(data), rule['min_size'])

    return True, ''


###table############################################
def stats_table(t_data):
    t_data['min_hc'] = 0
    t_data['max_hc'] = 0
    t_data['min_dc'] = 0
    t_data['max_dc'] = 0
    t_data['hrc'] = 0
    t_data['drc'] = 0
    t_data['hcc'] = 0
    t_data['dcc'] = 0
    if t_data['min_hc'] == t_data['max_hc']:
        t_data['hcc'] = t_data['min_hc']
    if t_data['min_dc'] == t_data['max_dc']:
        t_data['dcc'] = t_data['min_dc']

    if 'header' in t_data:
        t_data['hrc'] = len(t_data['header'])
        for item in t_data['header']:
            c = len(item)
            if t_data['min_hc'] == 0 or t_data['min_hc'] > c:
                t_data['min_hc'] = c
            if t_data['max_hc'] < c:
                t_data['max_hc'] = c
    if 'datas' in t_data:
        t_data['drc'] = len(t_data['datas'])
        for item in t_data['datas']:
            c = len(item)
            if t_data['min_dc'] == 0 or t_data['min_dc'] > c:
                t_data['min_dc'] = c
            if t_data['max_dc'] < c:
                t_data['max_dc'] = c


def parse_soup_table(table):
    result = {'header': [], 'datas': []}
    if table is None:
        return result
    if not table.thead is None:
        for tr in table.thead.children:
            if type(tr) != bs4.element.Tag and tr.name != 'tr':
                continue
            row = []
            for td in tr.children:
                if type(td) != bs4.element.Tag and (td.name != 'td' and td.name != 'th'):
                    continue
                row.append(td.text)
            result['header'].append(row)

    if not table.tbody is None:
        table = table.tbody

    for tr in table.children:
        if type(tr) != bs4.element.Tag and tr.name != 'tr':
            continue
        row = []
        for td in tr.children:
            if type(td) != bs4.element.Tag and (td.name != 'td' and td.name != 'th'):
                continue
            row.append(td.text)
        result['datas'].append(row)
    stats_table(result)
    return result


def check_table_filter(table, expr):
    return eval(expr)


# 处理验证码加减乘除202接口
def get_image_ocr_sum(img_content):
    # print(img_content)
    # img_content = base64.b64decode(img_content)
    base_s = base64.b64encode(img_content).decode()
    print(base_s)
    data = {'image': base_s}
    response = requests.post("http://192.168.1.202:1001/captcha", data=data)
    print(response.text)
    if '+' in response.text:
        res_list = response.text.split('+')
        return int(res_list[0])+int(res_list[1])
    if '加' in response.text:
        res_list = response.text.split('加')
        return int(res_list[0].strip())+int(res_list[1].strip())
    if '-' in response.text:
        res_list = response.text.split('-')
        return int(res_list[0]) - int(res_list[1])
    if '减' in response.text:
        res_list = response.text.split('减')
        return int(res_list[0].strip()) - int(res_list[1].strip())
    if 'x' in response.text:
        res_list = response.text.split('x')
        if res_list[0].isdigit() and res_list[1].isdigit():
            return int(res_list[0]) * int(res_list[1])
    if '乘' in response.text:
        res_list = response.text.split('乘')
        if res_list[0].isdigit() and res_list[1].isdigit():
            return int(res_list[0].strip()) * int(res_list[1].strip())
    if '/' in response.text:
        res_list = response.text.split('/')
        if res_list[0].isdigit() and res_list[1].isdigit():
            return int(res_list[0]) // int(res_list[1])
    return response.text

# 处理验证码202接口
def get_image_ocr(img_content):
    ocr = ddddocr.DdddOcr(beta=True)
    res = ocr.classification(img_content)
    return res


def cjy_dama(img_content, type):
    """
    img_content：图片的二进制
    type：打码类型
    详见官方文档：https://www.chaojiying.com/price.html
    对接打码平台
    :return:
    """
    # response = requests.get(url)
    if img_content:
        image = base64.b64encode(img_content)
        post_url = 'http://upload.chaojiying.net/Upload/Processing.php'
        # 定义参数字典
        data = {
            'user': 'whb123456',
            'pass': 'whb135264',
            'softid': '7a6a2314e8b90540fe9b168d5cdc7f23',
            'codetype': f'{type}',
            'file_base64': image
        }
        response = requests.post(url=post_url, data=data)
        # print(response.json()['pic_str'])
        return response.json()['pic_str']


def check_time(string, time_format="%Y-%m-%d"):
    if not string:
        return ''
    if isinstance(string, (int, float)):
        string = str(int(string))
    if not isinstance(string, str):
        raise TimeCheckError(f"时间格式化失败 {str(string)}")
    if string.isdigit():
        if len(string) == 13:
            return time.strftime(time_format, time.localtime(int(string)/1000))
        elif len(string) == 10:
            return time.strftime(time_format, time.localtime(int(string)))
        else:
            raise TimeCheckError(f"时间格式化失败 {str(string)}")
    string = string.strip()
    if '年' in string and '月' in string and '日' in string:
        string = string.split("日")[0]
        if "年" in time_format or '月' in time_format or '日' in time_format:
            t_format = time_format
        else:
            t_format = "%Y年%m月%d"
        try:
            d = datetime.datetime.strptime(string, t_format)
        except Exception as e:
            raise TimeCheckError(f"时间格式化失败 {string} -- {str(e)}")
    elif '年' in string and '月' in string:
        string = string.split(" ")[0]
        if "年" in time_format or '月' in time_format:
            t_format = time_format
        else:
            t_format = "%Y年%m月%d"
        try:
            d = datetime.datetime.strptime(string, t_format)
        except Exception as e:
            raise TimeCheckError(f"时间格式化失败 {string} -- {str(e)}")
    else:
        try:
            d = date_string_parser.parse(string)
        except Exception as e:
            raise TimeCheckError(f"时间格式化失败 {string} {str(e)}")
    return d.strftime(time_format)


def set_keys_value(obj, keys, value):
    if type(obj) != dict or type(keys) != list or len(keys) == 0:
        return
    temp = obj
    key_count = len(keys)
    for i in range(key_count -1):
        key = keys[i]
        if key in temp:
            if type(temp) != dict:
                return
        else:
            temp[key] = {}
        temp = temp[key]
    temp[keys[-1]] = value
    
def merge_config(base, add_para, keys = []):
    if type(base) != dict or type(add_para) != dict:
        return base
    for key, value in add_para.items():
        base_keys = keys.copy()
        base_keys.append(key)
        if type(value) == dict:
            merge_config(base, value, base_keys)
        else:
            set_keys_value(base, base_keys, value)

def get_pub_date(date_str):
    if date_str is None:
        return None
    if type(date_str) == datetime.date:
        return date_str
    if type(date_str) == datetime.datetime:
        return date_str.date()
    date_str = str(date_str)
    try:
        return parser.parse(date_str).date()
    except:
        pass
    try:
        res = re.findall('(\d{4})[年.-](\d{1,2})[月.-](\d{1,2})', date_str)
        if len(res) > 0:
            return datetime.date(int(res[0][0]),int(res[0][1]),int(res[0][2]))
    except:
        print("error pub_date", date_str)
        pass
    return None

def set_site_script(site_script):
    global md_site_script
    if site_script is None:
        return
    if len(site_script)>0:
        func_name = 'site_script_' + str(os.getpid())
        fp = open(func_name + '.py', 'w+')
        fp.write(site_script)
        fp.close()
        md_site_script = __import__(func_name)
        if os.path.exists(func_name + '.py'):
            os.remove(func_name + '.py')

def my_pad(text, pad_type='pkcs7', block_size=16):
    if text is None or type(text) != str:
        return None
    result = None
    text_len = len(text)
    if pad_type == 'pkcs7':
        pad_len = block_size - text_len%block_size;
        result = text + pad_len * chr(pad_len)
    elif pad_type == 'zero':
        if text_len % block_size != 0:
            result = text + (block_size - text_len % block_size) * chr(0)
        else:
            result = text
    
    return result

def my_unpad(text, pad_type='pkcs7'):
    if text is None or type(text) != str:
        return None
    result = None
    text_len = len(text)
    pad_len = 0
    if pad_type == 'pkcs7':
        pad_len = ord(text[-1])
    elif pad_type == 'zero':
        for i in range(text_len):
            if ord(text[-1 -i]) != 0:
                break
            pad_len += 1
    return text[:0-pad_len]

def encrypt_aes(key, text, text_pad_type='pkcs7', key_pad_type='zero', mode='ECB'):
    if mode == 'ECB':
        cipher = AES.new(my_pad(key, key_pad_type).encode(), AES.MODE_ECB)
    elif mode == 'CBC':
        cipher = AES.new(my_pad(key, key_pad_type).encode(), AES.MODE_CBC)
    else:
        return None
    result = make_base64(cipher.encrypt(my_pad(text).encode()))
    return result

def decrypt_aes(key, text, text_pad_type='pkcs7', key_pad_type='zero', mode='ECB'):
    if mode == 'ECB':
        cipher = AES.new(my_pad(key, key_pad_type).encode(), AES.MODE_ECB)
    elif mode == 'CBC':
        cipher = AES.new(my_pad(key, key_pad_type).encode(), AES.MODE_CBC)
    else:
        return None
    result = my_unpad(cipher.decrypt(base64.decodebytes(text.encode())).decode(), text_pad_type)
    return result
