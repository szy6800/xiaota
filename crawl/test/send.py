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
                "province": "",
                "city": "",
                "stage": ""
            },
            "dup_flag": 2,
            "page_list": {
                "module_name": "XTC_MOD_PAGE_LIST_A",
                "module_para": {
                    "req": {
                        "url": "http://fhq.zfzbw.cn/zhaobiao/",
                        "encoding": "utf-8"
                    },
                    "rule": {
                        "pick": {
                            "type": "xpath",
                            "pattern": "//*[@class=\"e-gr-w3-dn sub-mip-main\"]/div[contains(@class,'content')]",
                            "sub": {
                                "actions": [
                                    {
                                        "type": "set_value",
                                        "key": "docs.+.url",
                                        "expr": "str(values['xdata'].xpath(\".//a/@href\")[0])"
                                    },
                                    {
                                        "type": "set_value",
                                        "key": "docs.-1.encoding",
                                        "expr": "'utf-8'"
                                    },
                                    {
                                        "type": "set_value",
                                        "key": "docs.-1.purl",
                                        "expr": "obj['now_req']['url']"
                                    },
                                    {
                                        "type": "set_value",
                                        "key": "docs.-1.title",
                                        "expr": "str(values['xdata'].xpath(\".//a/@title\")[0])"
                                    },
                                    {
                                        "type": "set_value",
                                        "key": "docs.-1.pub_date",
                                        "expr": "str(values['xdata'].xpath('.//a/preceding::i[1]/text()')[0])"
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            "next_page": {
                "module_name": "XTC_MOD_NEXT_PAGE_FIX_URL",
                "module_para": {
                    "prefix": "http://fhq.zfzbw.cn/zhaobiao/lists_1_",
                    "expr": "int('%d'%(page))",
                    "postfix": ".html",
                    "rule": {
                        "pick": {
                            "type": "expr",
                            "pattern": "text",
                            "sub": {
                                "actions": [
                                    {
                                        "type": "set_value",
                                        "key": "info.total_page",
                                        "expr": "int(50)"
                                    }
                                ]
                            }
                        }
                    }
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
                "max_allow_fail_count": 30,
                "request_interval": 10

            }
        }

    )
    eval_string()
