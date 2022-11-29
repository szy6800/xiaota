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
        "url": "http://www.zgazxxw.com/zbpd/zhongbgg/index.html"
      },
      "rule": {
        "pick": {
          "type": "soup",
          "pattern": ".zx_marb",
          "sub": {
            "actions": [
              {
                "type": "set_value",
                "key": "docs.+.url",
                "expr": "values['soup'].select('.lt_title a:nth-last-child(1)')[0]['href']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.purl",
                "expr": "obj['now_req']['url']"
              },
              {
                "type": "set_value",
                "key": "docs.-1.title",
                "expr": "values['soup'].select('.lt_title a:nth-last-child(1)')[0].text"
              },
              {
                "type": "set_value",
                "key": "docs.-1.pub_date",
                "expr": "values['soup'].select('.fr')[0].text.split(' ')[-1]"
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
          "pattern": ".page a:nth-last-child(2)",
          "sub": {
                "actions": [
                  {
                    "type": "set_value",
                    "key": "next_reqs.+.url",
                    "expr": "values['soup']['href']"
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