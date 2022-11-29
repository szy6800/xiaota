# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Software: PyCharm
# __author__ == "YU HAIPENG"
# fileName: XTC_TASK_STD_ADD_OWR_REQ.py
# Month: 五月
# time: 2022/5/12 10:35
""" Write an introduction to the module here """

from .XTC_TASK_STD import *


class XTC_TASK_STD_ADD_OWR_REQ(XTC_TASK_STD):

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

        purl = get_value(req, 'purl', '')
        if purl != '':
            headers['Referer'] = purl
        req['url'] = get_full_url(req['url'], purl)
        self.logger.debug("%s XTC_TASK_STD request_url %s" % (self.site_info, req['url']))
        # print('request_url url=',req['url'], ' purl=', purl)
        self.step_info['req_url'] = req['url']

        for k, v in get_value(req, 'headers', {}).items():
            headers[k] = v

        files = get_value(req, 'files', None)

        method = get_value(req, 'method', 'get')

        req_paras = {'headers': headers}
        req_paras['timeout'] = 60

        if not self.proxies is None:
            req_paras['proxies'] = self.store.get_proxy(get_value(self.para['site_config'], 'proxy_key'))
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
                if para and "new_req_func" in para:
                    req_paras['url'] = req['url']
                    res = exec_string(para['new_req_func'], method=method, req_paras=req_paras, ori_session=self.req)
                else:
                    res = getattr(self.req, method)(req['url'], **req_paras)
                if res.status_code == 200:
                    break
            except Exception as ex:
                self.logger.error(self.site_info + traceback.format_exc())
                if i == self.request_retry_times - 1:
                    raise ex

        if len(res.content) < 2000000:
            encoding = get_value(req, 'encoding', None)
            charset = get_html_charset(res.text)
            if encoding is None:
                if charset:
                    res.encoding = charset
            elif encoding != '':
                res.encoding = encoding
        return res

