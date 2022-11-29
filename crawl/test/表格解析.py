#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @Author  : wlw
# @File    : 表格解析.py
# @Time    : 2022/3/25 15:25
#######################表格解析，内容添加到不同字段
{
  "filter": "data_col_count==4",
  "datas": {
    "source": "datas",
    "start": [
      0,
      0
    ],
    "end": [
      -1,
      1
    ],
    "reverse": "True"
  },
  "col_dict": {
    "合同编号": "",
    "项目编号": "project_no",
    "采购单位": "purchase_info_name",
    "项目辖区": "address",
    "代理机构": "agency_info_name",
    "供应商名称": "win_info_name",
    "合同签订日期": "winning_date"
  },
  "check_dict": {
    "type": "row",
    "data": "header",
    "idx": 1
  },
  "start": 1,
  "actions": [
    {
      "type": "set_value",
      "key": "project_no",
      "expr": "values['project_no'].strip()"
    },
    {
      "type": "set_value",
      "key": "purchase_info.name",
      "expr": "values['purchase_info_name'].strip()"
    },
    {
      "type": "set_value",
      "key": "address",
      "expr": "values['address'].strip()"
    },
    {
      "type": "set_value",
      "key": "agency_info.name",
      "expr": "values['agency_info_name'].strip()"
    },
    {
      "type": "set_value",
      "key": "win_info.name",
      "expr": "values['win_info_name'].strip()"
    },
    {
      "type": "set_value",
      "key": "winning_date",
      "expr": "values['winning_date'].strip()"
    }
  ]
}

