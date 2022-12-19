# encoding: UTF-8
import datetime
import time

import httpx
import json
from urllib.parse import quote

port_test = '8800'
port = '8100'

url_yhp = "http://192.168.1.202:%s/admin/system/check" % port_test
url_yhp_modify = "http://192.168.1.202:%s/admin//crawl/site/modifysave" % port_test

url = "http://192.168.1.202:%s/admin/system/check" % port
url_modify = "http://192.168.1.202:%s/admin//crawl/site/modifysave" % port


def send_test(conf):
    print(json.dumps(conf, indent=2, ensure_ascii=False))
    with httpx.Client() as session:
        session.post(
            url_yhp,
            data={
                "user_name": "admin",
                "user_pass": "xt123",
            }
        )

        session.post(
            url_yhp_modify,
            data={
                "site_name": conf.get('site_para', {}).get("source"),
                "site_desc": conf.get('site_para', {}).get("source"),
                "base_site_id": 0,
                "site_domain": conf.get('site_para', {}).get("source"),
                "platform": 0,
                "crawl_interval": "864000",
                "site_id": "991",
                "dev_user_id": "3005",
                "site_config": json.dumps(conf),
            }
        )


def eval_string():
    import psycopg2
    import psycopg2.extras
    import json
    db_conn = psycopg2.connect(host="192.168.1.201",
                               port='5432', user='postgres',
                               password='123456', database='analysis_crawl_test')
    db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # 这一段是将成功页数置为空，避免了每次新网站的页数累加
        db_cur.execute(
            "UPDATE tb_site SET crawl_para = '{}'  WHERE site_id = 137"
        )
        db_conn.commit()
    finally:
        db_cur.close()
        db_conn.close()


if __name__ == '__main__':
    false = False
    send_test(
        {
            "task_module": "XTC_TASK_STD",
            "site_para": {
                "province": "：山东省",
                "city": "",
                "stage": ""
            },
            "page_list": {
                "module_name": "XTC_MOD_PAGE_LIST_A",
                "module_para": {
                    "req": {
                        "url": "http://ggzyjyzx.shandong.gov.cn/module/web/jpage/dataproxy.jsp?startrecord=1&endrecord=54&perpage=18&unitid=474655&webid=428&path=http://ggzyjyzx.shandong.gov.cn/&webname=%E5%B1%B1%E4%B8%9C%E7%9C%81%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E4%B8%AD%E5%BF%83&col=1&columnid=209488&sourceContentType=1&permissiontype=0",
                        "encoding": "utf-8",
                        "method": "post",
                        "headers": {
                            "Accept": "application/xml, text/xml, */*; q=0.01",
                            "Accept-Encoding": "gzip, deflate",
                            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                            "Connection": "keep-alive",
                            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "Host": "ggzyjyzx.shandong.gov.cn",
                            "Origin": "http://ggzyjyzx.shandong.gov.cn",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36 Edg/103.0.1264.49",
                            "X-Requested-With": "XMLHttpRequest"
                        },
                        "data": {
                            "col": "1",
                            "webid": "428",
                            "path": "http://ggzyjyzx.shandong.gov.cn/",
                            "columnid": "209488",
                            "sourceContentType": "1",
                            "unitid": "474655",
                            "webname": "%E5%B1%B1%E4%B8%9C%E7%9C%81%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E4%B8%AD%E5%BF%83",
                            "permissiontype": "0"
                        }
                    },
                    "rules": [
                        {
                            "pick": {
                                "type": "xpath",
                                "pattern": "//recordset/record",
                                "sub": {
                                    "not_filter": "1370364_310032240|art_1370364_31003224|art_209488_10389764|art_209488_10378261",
                                    "actions": [
                                        {
                                            "type": "set_value",
                                            "key": "docs.+.url",
                                            "expr": "def eval_string(obj, values):\n    if 'http' in str(values['xdata'].xpath('.//a/@href')[0]):\n        return str(values['xdata'].xpath('.//a/@href')[0])\n    else:\n        return 'http://www.zhuji.gov.cn' + str(values['xdata'].xpath('.//a/@href')[0])"
                                        },
                                        {
                                            "type": "set_value",
                                            "key": "docs.-1.title",
                                            "expr": "str(values['xdata'].xpath('.//a/@title')[0])"
                                        },
                                        {
                                            "type": "set_value",
                                            "key": "docs.-1.pub_date",
                                            "expr": "str(values['xdata'].xpath('.//span/text()')[0]).strip()"
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            },
            "next_page": {
                "module_name": "XTC_MOD_NEXT_PAGE_FIX_URL",
                "module_para": {
                    "prefix": "http://ggzyjyzx.shandong.gov.cn/module/web/jpage/dataproxy.jsp?startrecord=",
                    "expr": "'%d&endrecord=%d&perpage=18'%(page-53,page)",
                    "postfix": "&unitid=474655&webid=428&path=http://ggzyjyzx.shandong.gov.cn/&webname=%E5%B1%B1%E4%B8%9C%E7%9C%81%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E4%B8%AD%E5%BF%83&col=1&columnid=209488&sourceContentType=1&permissiontype=0",
                    "method": "post",
                    "post_para": {
                        "col": "1",
                        "webid": "428",
                        "path": "http://ggzyjyzx.shandong.gov.cn/",
                        "columnid": "209488",
                        "sourceContentType": "1",
                        "unitid": "474655",
                        "webname": "%E5%B1%B1%E4%B8%9C%E7%9C%81%E5%85%AC%E5%85%B1%E8%B5%84%E6%BA%90%E4%BA%A4%E6%98%93%E4%B8%AD%E5%BF%83",
                        "permissiontype": "0"
                    },
                    "rules": [
                        {
                            "pick": {
                                "type": "xpath",
                                "pattern": "//totalpage",
                                "sub": {
                                    "actions": [
                                        {
                                            "type": "set_value",
                                            "key": "info.total_page",
                                            "expr": "math.ceil(int(values['xdata'].xpath('./text()')[0])/3)*54"
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            },
            "content": {
                "module_para": {
                    "rules": [
                        {
                            "picks": [
                                {
                                    "type": "xpath",
                                    "pattern": "//a[contains(text(), '.PDF') or contains(text(), '.JPEG') or contains(text(), '.JPG') or contains(text(), '.RAR') or contains(text(), '.DOCX') or contains(text(), '.XLSX') or contains(text(), '.XLS') or contains(text(), '.ZIP') or contains(text(), '.PNG') or contains(text(), '.DOC') or  contains(text(), '.GZSZB') or contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(@href,'.pdf') or contains(@href,'.jpeg') or contains(@href,'.jpg') or contains(@href,'.rar') or contains(@href,'.docx') or contains(@href,'.xlsx') or contains(@href,'.xls') or contains(@href,'.zip') or contains(@href,'.png') or contains(@href,'.doc') or contains(@href,'.GZSZB') or contains(@href,'.PDF') or contains(@href,'.JPEG') or contains(@href,'.JPG') or contains(@href,'.RAR') or contains(@href,'.DOCX') or contains(@href,'.XLSX') or contains(@href,'.XLS') or contains(@href,'.ZIP') or contains(@href,'.PNG') or contains(@href,'.DOC')]",
                                    "sub": {
                                        "not_filter": "javascript:window.close()|javascript:doPrint()|mailto|javascript:downPList()|javascript:void",
                                        "actions": [
                                            {
                                                "key": "reqs.+.url",
                                                "type": "set_value",
                                                "expr": "values['xdata'].attrib['href']"
                                            },
                                            {
                                                "key": "reqs.-1.purl",
                                                "type": "set_value",
                                                "expr": "obj['now_req']['url']"
                                            },
                                            {
                                                "key": "reqs.-1.allow_error_level",
                                                "type": "set_value",
                                                "expr": "2"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                },
                "module_name": "XTC_MOD_CONTENT_STD",
                "start_pub_date": "2021-01-01",
                "verify": false,
                "max_allow_fail_count": 150,
                "request_interval": 10
            }
        }

    )
    eval_string()
