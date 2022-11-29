{
  "task_module": "XTC_TASK_STD",
  "site_para": {
    "area": "北京"
  },
  "stop_filter": "run_times>5",
  "page_list": {
    "module_name": "XTC_MOD_PAGE_LIST_A",
    "module_para": {
      "req": {
        "url": "https://ggzyfw.beijing.gov.cn/jyxxggjtbyqs/index.html"
      },
      "rule": {
        "pick": {
          "type": "soup",
          "pattern": "ul[class='article-listjy2'] > li",
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
                "expr": "values['soup'].div.p.text.strip()"
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
          "pattern": "a:contains(下一页)",
          "sub": {
            "pick": {
              "type": "re",
              "pattern": "onclick=\"location.href=encodeURI\\('(.*?)'\\);\">下一页",
              "sub": {
                "actions": [
                  {
                    "type": "set_value",
                    "key": "next_reqs.+.url",
                    "expr": "values['values']"
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
      }
    }
  },
  "content": {
    "module_name": "XTC_MOD_CONTENT_STD",
    "module_para": {}
  }
}