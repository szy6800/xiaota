{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": ""
  },
  "stop_filter": "run_times>5",
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "https://buy.cnooc.com.cn/cbjyweb/001/001002/1.html"
      },
      "rule": {
        "pick": {
          "type": "soup",
          "pattern": ".now-hd-items li",
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
                "expr": "values['soup'].a['title']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "values['soup'].span.text"
              }
            ]
          }
        }
      }
    }
  },
  "next_page": {
    "module_name": "XTC_MOD_NEXT_PAGE_URL",
    "module_para": {
      "rule": {
        "pick": {
          "type": "soup",
          "pattern": ".page",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "next_reqs.+.url",
                "expr": "values['soup'].select('a:nth-child(3)')[0]['href']"
              },
              {
                "type": "set_value",
                "key": "next_reqs.-1.purl",
                "expr": "obj['now_req']['url']"
              }
            ]
          }
        }
      }
    }
  },
  "content": {
    "module_name": "XTC_MOD_CONTENT_STD",
    "module_para": {}
  }
}