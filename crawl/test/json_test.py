{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": "浙江"
  },
  "stop_filter": "run_times>2",
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "post_para": {
        "apicode": "GetNoticeList",
        "args": {
          "columnId": "82",
          "contentType": 1,
          "pageIndex": 1,
          "pageSize": 20,
          "maxCount": 170,
          "subjectId": 0
        },
        "deviceinfo": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "token": "dreamtouch"
      },
      "req": {
        "url": "http://www.hospitalstar.com/noticelist?cid=82&fnav=7#anchor"
      },
      "rules": [
        {
          "url_filter": "http://www.hospitalstar.com/noticelist",
          "actions": [
            {
              "type": "set_value",
              "key": "reqs.+.url",
              "expr": "\"http://47.110.151.141:8001/hs/api?timeStamp=%s\"%(int(time.time()*1000))"
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
              "key": "reqs.-1.json",
              "expr": "obj['para']['post_para']"
            }
          ]
        },
        {
          "url_filter": "http://47.110.151.141:8001/hs/api",
          "pick": {
            "type": "json",
            "pattern": "jdata['data']['noticeList']",
            "sub": {
              "actions": [
                {
                  "type": "set_value",
                  "key": "docs.+.url",
                  "expr": "'http://www.hospitalstar.com/newsdetail?fnav=7&noticeId=%s&title='%(values['jdata']['noticeId'])"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.title",
                  "expr": "values['jdata']['noticeTitle']"
                },
                {
                  "type": "set_value",
                  "key": "docs.-1.noticeId",
                  "expr": "values['jdata']['noticeId']"
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
      "expr": "\"http://47.110.151.141:8001/hs/api?timeStamp=%s\"%(int(time.time()*1000))",
      "method": "post",
      "post_para": {
        "apicode": "GetNoticeList",
        "args": {
          "columnId": "82",
          "contentType": 1,
          "pageIndex": 1,
          "pageSize": 20,
          "maxCount": 170,
          "subjectId": 0
        },
        "deviceinfo": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "token": "dreamtouch"
      },
      "post_key": "json",
      "req_expr": "simple_set_key_value(json['args'],'pageIndex',page)",
      "rule": {
        "url_filter": "http://47.110.151.141:8001/hs/api",
        "pick": {
          "type": "json",
          "pattern": "jdata['data']['totalCount']",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "info.total_record",
                "expr": "int(values['jdata'])"
              },
              {
                "type": "set_value",
                "key": "info.total_page",
                "expr": "math.ceil(int(values['jdata'])/20)"
              }
            ]
          }
        }
      }
    }
  },
  "content": {
    "module_name": "XTC_MOD_CONTENT_STD",
    "module_para": {
      "post_para": {
        "apicode": "GetNoticeDetail",
        "args": {
          "noticeId": "",
          "columnId": 0,
          "subjectId": 0
        },
        "deviceinfo": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "token": "dreamtouch"
      },
      "rules": [
        {
          "url_filter": "http://www.hospitalstar.com/newsdetail",
          "actions": [
            {
              "type": "set_value",
              "key": "reqs.+.url",
              "expr": "\"http://47.110.151.141:8001/hs/api?timeStamp=%s\"%(int(time.time()*1000))"
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
              "key": "para.post_para.args.noticeId",
              "expr": "obj['now_req']['noticeId']"
            },
            {
              "type": "set_value",
              "key": "reqs.-1.json",
              "expr": "obj['para']['post_para']"
            },
            {
              "type": "set_value",
              "key": "reqs.-1.ctype",
              "expr": "'json'"
            }
          ]
        },
        {
          "url_filter": "http://47.110.151.141:8001/hs/api",
          "pick": {
            "type": "json",
            "pattern": "jdata['data']['noticeContent']",
            "sub": {
              "pick": {
                "type": "soup",
                "pattern": "a",
                "sub": {
                  "not_filter": "mailto",
                  "actions": [
                    {
                      "type": "set_value",
                      "key": "reqs.+.url",
                      "expr": "values['soup']['href']"
                    },
                    {
                      "type": "set_value",
                      "key": "reqs.-1.purl",
                      "expr": "obj['now_req']['purl']"
                    },
                    {
                      "type": "set_value",
                      "key": "reqs.-1.title",
                      "expr": "values['soup'].text"
                    }
                  ]
                }
              }
            }
          }
        }
      ]
    }
  }
}