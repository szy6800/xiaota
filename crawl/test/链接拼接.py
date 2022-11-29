{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": "华西"
  },
  "stop_filter": "run_times>3",
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "https://www.hxyc.com.cn/portal/list.do?chnlcode=tender&objtypepl=2&kw=&dw=&chnlvo.pagestr=1&chnlvo.pageSize=10"
      },
      "rule": {
        "pick": {
          "type": "soup",
          "pattern": "div[class='product prolist notice list'] > ul > li",
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
                "expr": "values['soup'].a.dl.dt.p.text.strip()"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "values['soup'].a.dd.span[class='h-info'].text.strip()"
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
      "prefix": "https://www.hxyc.com.cn/portal/list.do?chnlcode=tender&objtypepl=2&kw=&dw=&chnlvo.pageSize=10&chnlvo.pagestr=",
      "expr": "'%d'%(page)",
      "order": "asc",
      "rule": {
        "pick": {
          "type": "re",
          "pattern": "共(.*?)条",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "info.total_page",
                "expr": "int(float(values['values'])/20)"
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
      "rule": {
        "pick": {
          "type": "soup",
          "pattern": "a:contains(附件)",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "reqs.+.url",
                "expr": "values['soup']['href']"
              },
              {
                "type": "set_value",
                "key": "reqs.-1.purl",
                "expr": "obj['now_req']['url']"
              }
            ]
          }
        }
      }
    }
  }
}