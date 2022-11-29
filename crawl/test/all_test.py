#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @Author  : wlw
# @File    : all_test.py
# @Time    : 2022/2/18 16:06


#######################get请求，xpath解析；get请求拼接字符串，正则提取最大页
{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": ""
  },
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "http://bid.cncecyc.com/cms/channel/ywgg3jt/index.htm?pageNo=1"
      },
      "rule": {
        "pick": {
          "type": "xpath",
          "pattern": "//ul[@id=\"list1\"]/li",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "docs.+.url",
                "expr": "str(values['xdata'].xpath('.//a/@href')[0])"
              },
              {
                "type": "set_value",
                "key": "docs.-1.purl",
                "expr": "obj['now_req']['url']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.title",
                "expr": "str(values['xdata'].xpath('.//a/text()')[0])"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "str(values['xdata'].xpath('.//span[@class=\"bidDate\"]/text()')[0])"
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
      "prefix": "http://bid.cncecyc.com/cms/channel/ywgg3jt/index.htm?pageNo=",
      "expr": "'%d'%(page)",
      "postfix": "",
      "order": "asc",
      "rule": {
        "pick": {
          "type": "re",
          "pattern": "共计<em>(.*?)</em>页",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "info.total_page",
                "expr": "int(values['values'])"
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
              "pattern": "//a[contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(@href,'.pdf') or contains(@href,'.jpeg') or contains(@href,'.jpg') or contains(@href,'.rar') or contains(@href,'.docx') or contains(@href,'.xlsx') or contains(@href,'.xls') or contains(@href,'.zip') or contains(@href,'.png') or contains(@href,'.doc') or contains(@href,'.GZSZB')",
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
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    "module_name": "XTC_MOD_CONTENT_STD"
  }
}
#######################get请求，json解析加json解析；get请求拼接字符串，json指定最大页
{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": "江苏省"
  },
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "http://njggzy.nanjing.gov.cn/webdb_njggzy/fjszListAction.action?cmd=getxqylist&categorynum=067006002&keyword=&winbiddername=&pageIndex=1&pageSize=10"
      },
      "rule": {
        "pick": {
          "type": "json",
          "pattern": "json.loads(jdata['custom'])['Table']",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "docs.+.url",
                "expr": "'http://njggzy.nanjing.gov.cn%s'%(values['jdata']['href'])"
              },
              {
                "type": "set_value",
                "key": "docs.-1.title",
                "expr": "values['jdata']['title']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "values['jdata']['infodate']"
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
      "prefix": "http://njggzy.nanjing.gov.cn/webdb_njggzy/fjszListAction.action?cmd=getxqylist&categorynum=067006002&keyword=&winbiddername=&pageIndex=",
      "expr": "'%d'%(page+1)",
      "postfix": "&pageSize=10",
      "order": "asc",
      "rule": {
        "pick": {
          "type": "json",
          "pattern": "jdata['custom']",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "info.total_page",
                "expr": "int(46)"
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
              "pattern": "//a[contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(@href,'.pdf') or contains(@href,'.jpeg') or contains(@href,'.jpg') or contains(@href,'.rar') or contains(@href,'.docx') or contains(@href,'.xlsx') or contains(@href,'.xls') or contains(@href,'.zip') or contains(@href,'.png') or contains(@href,'.doc') or contains(@href,'.GZSZB') or contains(@href,'download') or contains(@href,'upload')]",
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
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    "module_name": "XTC_MOD_CONTENT_STD"
  }
}
#######################get请求，json解析加json解析；get请求拼接字符串，json获取最大页
{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "province": "浙江",
    "city": "",
    "stage": "采购公告"
  },
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "http://igotone.zj.chinamobile.com:188/rc-portal/portal/home/purchase_notice/all?timestamp=1648864449221&pageSize=6&pageNum=1"
      },
      "rule": {
        "pick": {
          "type": "json",
          "pattern": "jdata['data']['list']",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "docs.+.url",
                "expr": "'http://igotone.zj.chinamobile.com:188/rc-portal/portal/home/purchase_notice/%s'%(values['jdata']['id'])"
              },
              {
                "type": "set_value",
                "key": "docs.-1.title",
                "expr": "values['jdata']['title']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "values['jdata']['publishDate']"
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
      "prefix": "http://igotone.zj.chinamobile.com:188/rc-portal/portal/home/purchase_notice/all?timestamp=1648864449221&pageSize=6&pageNum=",
      "expr": "'%d'%(page+1)",
      "postfix": "",
      "order": "asc",
      "rule": {
        "pick": {
          "type": "json",
          "pattern": "jdata['data']['pages']",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "info.total_page",
                "expr": "int(values['jdata'])"
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
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    "module_name": "XTC_MOD_CONTENT_STD"
  }
}
#######################post请求，xpath解析；post请求，自定义最大页码
{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": "安徽"
  },
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "http://www.ahtba.org.cn/site/trade/affiche/pageList",
        "encoding": "utf-8",
        "method": "post",
        "json": {"pubTime":"","tradeType":"02","tradeClassify":"","regionCode":"","afficheSourceType":"","afficheTitle":"","pageNum":1,"pageSize":10}
      },
      "rule": {
        "pick": {
          "type": "xpath",
          "pattern": "//div[@class=\"rightBoxList\"]//li",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "docs.+.url",
                "expr": "'http://www.ahtba.org.cn/htmlUrl/trade_/'+str(values['xdata'].xpath('.//div[@class=\"fr nums\"]/text()')[0])+'/'+str(values['xdata'].xpath('.//a/@href')[0]).split('/')[-1]+'.html'"
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
                "expr": "str(values['xdata'].xpath('.//a/text()')[0])"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "str(values['xdata'].xpath('.//div[@class=\"fr nums\"]/text()')[0])"
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
      "order": "asc",
      "expr": "'http://www.ahtba.org.cn/site/trade/affiche/pageList'",
      "method": "post",
      "post_para": {"pubTime":"","tradeType":"02","tradeClassify":"","regionCode":"","afficheSourceType":"","afficheTitle":"","pageNum":1,"pageSize":10},
      "post_key": "json",
      "req_expr": "simple_set_key_value(json,'pageNum',page)",
      "rules": [
        {
          "pick": {
            "type": "xpath",
            "pattern": "//div[@class=\"rightBoxList\"]//li",
            "sub": {
              "actions": [
                {
                  "type": "set_value",
                  "key": "info.total_page",
                  "expr": "int(3303)"
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
              "pattern": "//a[contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(@href,'.pdf') or contains(@href,'.jpeg') or contains(@href,'.jpg') or contains(@href,'.rar') or contains(@href,'.docx') or contains(@href,'.xlsx') or contains(@href,'.xls') or contains(@href,'.zip') or contains(@href,'.png') or contains(@href,'.doc') or contains(@href,'.GZSZB') or contains(@href,'download') or contains(@href,'upload')]",
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
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    "module_name": "XTC_MOD_CONTENT_STD"
  }
}
#######################post请求，参数data，xpath解析；post请求，正则提取最大页
{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "province": "内蒙古自治区",
    "city": "",
    "stage": ""
  },
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "http://ggzyjy.nmg.gov.cn/jyxx/zfcg/cggg",
        "encoding": "utf-8",
        "method": "post",
        "data": {
          "currentPage": "1",
          "time": "",
          "industriesTypeCode": "",
          "scrollValue": "1083",
          "bulletinTitle": "",
          "area": "",
          "startTime": "",
          "endTime": ""
        }
      },
      "rule": {
        "pick": {
          "type": "xpath",
          "pattern": "//div[@class=\"content_right fr\"]//tr/td/parent::tr",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "docs.+.url",
                "expr": "str(values['xdata'].xpath('.//a/@href')[0])"
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
                "expr": "str(values['xdata'].xpath('.//a/@title')[0])"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "str(values['xdata'].xpath('.//td[4]/text()')[0]).strip()"
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
      "order": "asc",
      "expr": "'http://ggzyjy.nmg.gov.cn/jyxx/zfcg/cggg'",
      "method": "post",
      "post_para": {
        "currentPage": "1",
        "time": "",
        "industriesTypeCode": "",
        "scrollValue": "1083",
        "bulletinTitle": "",
        "area": "",
        "startTime": "",
        "endTime": ""
      },
      "post_key": "data",
      "req_expr": "simple_set_key_value(data,'currentPage',page)",
      "rules": [
        {
          "pick": {
            "type": "re",
            "pattern": "共(\\d+)页",
            "sub": {
              "actions": [
                {
                  "type": "set_value",
                  "key": "info.total_page",
                  "expr": "int(values['values'])"
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
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    "module_name": "XTC_MOD_CONTENT_STD"
  }
}
#######################post请求，参数data+json.dumps；构造二次请求
{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": "安徽"
  },
  "stop_filter": "run_times>5",
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "post_para": {
        "args": {
          "siteGuid": "7eb5f7f1-9041-43ad-8e13-8fcb82ea831a",
          "categoryNum": "005002",
          "keyword": "",
          "startDate": "",
          "endDate": "",
          "publishDate": "",
          "area": "",
          "tradeType": "",
          "pageIndex": 0,
          "pageSize": 12
        }
      },
      "reqs": [
        {
          "url": "https://ggzy.chuzhou.gov.cn/jiaoyixinxi/005002/bussinessiBulid.html?cnum=005002003"
        }
      ],
      "rules": [
        {
          "url_filter": "https://ggzy.chuzhou.gov.cn/jiaoyixinxi/005002/bussinessiBulid.html\\?cnum=005002003",
          "actions": [
            {
              "type": "set_value",
              "key": "reqs.+.url",
              "expr": "'https://ggzy.chuzhou.gov.cn/EpointWebBuilder/rest/GgSearchAction/getInfoMationList'"
            },
            {
              "type": "set_value",
              "key": "reqs.-1.purl",
              "expr": "obj['now_req']['url']"
            },
            {
              "type": "set_value",
              "key": "reqs.-1.method",
              "expr": "'post'"
            },
            {
              "type": "set_value",
              "key": "reqs.-1.data",
              "expr": "{'params':json.dumps(obj['para']['post_para']['args'])}"
            }
          ]
        },
        {
          "url_filter": "https://ggzy.chuzhou.gov.cn/EpointWebBuilder/rest/GgSearchAction/getInfoMationList",
          "pick": {
            "type": "json",
            "pattern": "jdata['Table']",
            "sub": {
              "actions": [
                {
                  "type": "set_value",
                  "key": "docs.+.url",
                  "expr": "'https://ggzy.chuzhou.gov.cn/jiaoyixinxi/%s/%s/%s/%s.html'%(values['jdata']['categorynum'][:6],values['jdata']['categorynum'],values['jdata']['infodate'].replace('-',''),values['jdata']['infoId'])"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.purl",
                  "expr": "obj['now_req']['url']"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.title",
                  "expr": "values['jdata']['title']"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.pub_date",
                  "expr": "values['jdata']['infodate']"
                },
                {
                  "type": "set_value",
                  "key": "reqs.-1.data",
                  "expr": "{'params':json.dumps(obj['para']['post_para']['args'])}"
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
      "order": "asc",
      "expr": "'https://ggzy.chuzhou.gov.cn/EpointWebBuilder/rest/GgSearchAction/getInfoMationList'",
      "method": "post",
      "post_para": {
        "pageNumber": "1",
        "keyWord": "",
        "timeType": "",
        "rangeCode": "",
        "typeCode": "4",
        "capitalSourceCode": "",
        "industryCode": "",
        "provinceCode": ""
      },
      "post_key": "data",
      "rule": {
        "url_filter": "https://ggzy.chuzhou.gov.cn/EpointWebBuilder/rest/GgSearchAction/getInfoMationList",
        "pick": {
          "type": "json",
          "pattern": "jdata",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "info.total_page",
                "expr": "int(values['jdata']['RowCount'])"
              },
              {
                "type": "set_value",
                "key": "para.params",
                "expr": "json.loads(obj['now_req']['data']['params'])"
              },
              {
                "type": "set_value",
                "key": "para.test",
                "expr": "simple_set_key_value(obj['para']['params'],'pageIndex',int(values['jdata']['PageIndex']+1))"
              },
              {
                "type": "set_value",
                "key": "para.post_para",
                "expr": "{'params':json.dumps(obj['para']['params'])}"
              },
              {
                "type": "set_value",
                "key": "obj.para.post_para",
                "expr": "{'params':json.dumps(obj['para']['params'])}"
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
              "pattern": "//a[contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(@href,'.pdf') or contains(@href,'.jpeg') or contains(@href,'.jpg') or contains(@href,'.rar') or contains(@href,'.docx') or contains(@href,'.xlsx') or contains(@href,'.xls') or contains(@href,'.zip') or contains(@href,'.png') or contains(@href,'.doc') or contains(@href,'.GZSZB') or contains(@href,'download') or contains(@href,'upload')]",
              "sub": {
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
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    "module_name": "XTC_MOD_CONTENT_STD"
  }
}
#######################使用module_expr案例
{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": "安徽"
  },
  "stop_filter": "run_times>5",
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "post_para": {
        "categorymum": "001",
        "sdt": "",
        "edt": "",
        "tbsdt": "",
        "tbedt": "",
        "title": "",
        "cgzz": "",
        "cgfs": "",
        "pageSize": 20,
        "pageIndex": -1,
        "siteguid": "7eb5f7f1-9041-43ad-8e13-8fcb82ea831a"
      },
      "module_expr": "simple_set_key_value(obj['para']['post_para'],'pageIndex',obj['para']['post_para']['pageIndex']+1)",
      "reqs": [
        {
          "url": "https://bid.zyepp.com/zbzq/listjyxx.html?categoryNum=001&pageIndex=215"
        }
      ],
      "rules": [
        {
          "url_filter": "https://bid.zyepp.com/zbzq/listjyxx.html\\?categoryNum=001&pageIndex=215",
          "actions": [
            {
              "type": "set_value",
              "key": "reqs.+.url",
              "expr": "'https://bid.zyepp.com/EpointWebBuilder/rest/infolist/geInfoListZZ'"
            },
            {
              "type": "set_value",
              "key": "reqs.-1.purl",
              "expr": "obj['now_req']['url']"
            },
            {
              "type": "set_value",
              "key": "reqs.-1.method",
              "expr": "'post'"
            },
            {
              "type": "set_value",
              "key": "reqs.-1.data",
              "expr": "{'params':json.dumps(obj['para']['post_para'])}"
            }
          ]
        },
        {
          "url_filter": "https://bid.zyepp.com/EpointWebBuilder/rest/infolist/geInfoListZZ",
          "pick": {
            "type": "json",
            "pattern": "jdata['Table']",
            "sub": {
              "actions": [
                {
                  "type": "set_value",
                  "key": "docs.+.url",
                  "expr": "'https://bid.zyepp.com%s'%(values['jdata']['infourl'])"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.purl",
                  "expr": "obj['now_req']['url']"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.title",
                  "expr": "values['jdata']['title']"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.pub_date",
                  "expr": "values['jdata']['infodate']"
                },
                {
                  "type": "set_value",
                  "key": "reqs.-1.data",
                  "expr": "{'params':json.dumps(obj['para']['post_para'])}"
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
      "order": "asc",
      "expr": "'https://bid.zyepp.com/EpointWebBuilder/rest/infolist/geInfoListZZ'",
      "method": "post",
      "post_para": {
        "categorymum": "001",
        "sdt": "",
        "edt": "",
        "tbsdt": "",
        "tbedt": "",
        "title": "",
        "cgzz": "",
        "cgfs": "",
        "pageSize": 20,
        "pageIndex": 0,
        "siteguid": "7eb5f7f1-9041-43ad-8e13-8fcb82ea831a"
      },
      "post_key": "data",
      "rule": {
        "url_filter": "https://bid.zyepp.com/EpointWebBuilder/rest/infolist/geInfoListZZ",
        "pick": {
          "type": "json",
          "pattern": "jdata",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "info.total_page",
                "expr": "int(int(values['jdata']['RowCount'])/20)"
              },
              {
                "type": "set_value",
                "key": "para.params",
                "expr": "json.loads(obj['now_req']['data']['params'])"
              },
              {
                "type": "set_value",
                "key": "para.test",
                "expr": "simple_set_key_value(obj['para']['params'],'pageIndex',int(values['jdata']['PageIndex']+1))"
              },
              {
                "type": "set_value",
                "key": "para.post_para",
                "expr": "{'params':json.dumps(obj['para']['params'])}"
              },
              {
                "type": "set_value",
                "key": "obj.para.post_para",
                "expr": "{'params':json.dumps(obj['para']['params'])}"
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
              "pattern": "//a[contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(@href,'.pdf') or contains(@href,'.jpeg') or contains(@href,'.jpg') or contains(@href,'.rar') or contains(@href,'.docx') or contains(@href,'.xlsx') or contains(@href,'.xls') or contains(@href,'.zip') or contains(@href,'.png') or contains(@href,'.doc') or contains(@href,'.GZSZB') or contains(@href,'download') or contains(@href,'upload')]",
              "sub": {
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
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    "module_name": "XTC_MOD_CONTENT_STD"
  }
}
#######################time修改data参数
{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": ""
  },
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "http://deal.ggzy.gov.cn/ds/deal/dealList_find.jsp",
        "method": "post",
        "data": {
          "TIMEBEGIN_SHOW": "2021-12-09",
          "TIMEEND_SHOW": "2022-03-09",
          "TIMEBEGIN": "2021-12-09",
          "TIMEEND": "2022-03-09",
          "SOURCE_TYPE": "1",
          "DEAL_TIME": "05",
          "DEAL_CLASSIFY": "00",
          "DEAL_STAGE": "0000",
          "DEAL_PROVINCE": "0",
          "DEAL_CITY": "0",
          "DEAL_PLATFORM": "0",
          "BID_PLATFORM": "0",
          "DEAL_TRADE": "0",
          "isShowAll": "1",
          "PAGENUMBER": "1",
          "FINDTXT": ""
        }
      },
      "rules": [
        {
          "pick": {
            "type": "json",
            "pattern": "jdata['data']",
            "sub": {
              "actions": [
                {
                  "type": "set_value",
                  "key": "docs.+.url",
                  "expr": "str(values['jdata']['url'])"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.title",
                  "expr": "values['jdata']['title']"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.pub_date",
                  "expr": "values['jdata']['timeShow']"
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
      "order": "asc",
      "expr": "'http://deal.ggzy.gov.cn/ds/deal/dealList_find.jsp'",
      "method": "post",
      "post_para": {
        "TIMEBEGIN_SHOW": "2021-12-09",
        "TIMEEND_SHOW": "2022-03-09",
        "TIMEBEGIN": "2021-12-09",
        "TIMEEND": "2022-03-09",
        "SOURCE_TYPE": "1",
        "DEAL_TIME": "06",
        "DEAL_CLASSIFY": "00",
        "DEAL_STAGE": "0000",
        "DEAL_PROVINCE": "0",
        "DEAL_CITY": "0",
        "DEAL_PLATFORM": "0",
        "BID_PLATFORM": "0",
        "DEAL_TRADE": "0",
        "isShowAll": "1",
        "PAGENUMBER": "1",
        "FINDTXT": ""
      },
      "post_key": "data",
      "req_expr": "simple_set_key_value(obj['para']['post_para'],'PAGENUMBER',page+1)",
      "rules": [
        {
          "pick": {
            "type": "re",
            "pattern": "ttlrow",
            "sub": {
              "actions": [
                {
                  "type": "set_value",
                  "key": "para.post_para.TIMEEND_SHOW",
                  "expr": "time.strftime('%Y-%m-%d', time.localtime(int(time.time())))"
                },
                {
                  "type": "set_value",
                  "key": "para.post_para.TIMEEND",
                  "expr": "time.strftime('%Y-%m-%d', time.localtime(int(time.time())))"
                },
                {
                  "type": "set_value",
                  "key": "para.post_para.TIMEBEGIN_SHOW",
                  "expr": "time.strftime('%Y-%m-%d', time.localtime(int(time.time())-7776000))"
                },
                {
                  "type": "set_value",
                  "key": "para.post_para.TIMEBEGIN",
                  "expr": "time.strftime('%Y-%m-%d', time.localtime(int(time.time())-7776000))"
                }
              ]
            }
          }
        },
        {
          "pick": {
            "type": "json",
            "pattern": "jdata['ttlpage']",
            "sub": {
              "actions": [
                {
                  "type": "set_value",
                  "key": "info.total_page",
                  "expr": "int(values['jdata'])"
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
              "pattern": "//a[contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(text(), '.pdf') or contains(text(), '.jpeg') or contains(text(), '.jpg') or contains(text(), '.rar') or contains(text(), '.docx') or contains(text(), '.xlsx') or contains(text(), '.xls') or contains(text(), '.zip') or contains(text(), '.png') or contains(text(), '.doc') or contains(text(), '.GZSZB') or contains(@href,'.pdf') or contains(@href,'.jpeg') or contains(@href,'.jpg') or contains(@href,'.rar') or contains(@href,'.docx') or contains(@href,'.xlsx') or contains(@href,'.xls') or contains(@href,'.zip') or contains(@href,'.png') or contains(@href,'.doc') or contains(@href,'.GZSZB') or contains(@href,'download') or contains(@href,'upload')]",
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
                  }
                ]
              }
            }
          ]
        }
      ]
    },
    "module_name": "XTC_MOD_CONTENT_STD"
  }
}