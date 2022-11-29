# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Software: PyCharm
# __author__ == "YU HAIPENG"
# fileName: configure_model.py
# Month: 一月
# time: 2022/1/13 17:03
"""
任务 SQL基础配制参数 统一化
"""
import json
import datetime as structure_datetime
import copy


class MyJSONEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, structure_datetime.datetime):
            return str(o)


class Base(object):
    """ 数据结构 基类 """

    def __setitem__(self, key, value):
        self.__dict__[key] = value.strip() if isinstance(value, str) else value

    def __getitem__(self, item):
        return self.__dict__[item]

    def __getattr__(self, item):
        try:
            value = super().__getattr__(item)
        except AttributeError:
            return getattr(self.__dict__, item)
        return value

    def __setattr__(self, key, value):
        self.__dict__[key] = value.strip() if isinstance(value, str) else value

    def __str__(self):
        string = json.dumps(self.to_dict, ensure_ascii=False, indent=2, cls=MyJSONEncoder)
        return string

    def __repr__(self):
        return self.__str__()

    def get(self, item, default=None):
        try:
            res = self[item]
        except KeyError:
            return default
        else:
            return res

    @property
    def to_dict(self):
        d = copy.deepcopy(self.__dict__)
        for k, v in d.items():
            if isinstance(v, ParamsPreparation):
                d[k] = v.to_dict
        return d

    def dumps(self):
        return json.dumps(self.to_dict, cls=MyJSONEncoder)


class ConfigureModel(Base):
    """
    任务配制基础参数类
    """

    def __init__(
            self,
            page_list=None,  # type:  [ParamsPreparation, str, dict]
            next_page=None,  # type: [ParamsPreparation, str, dict]
            content=None,  # type:  [ParamsPreparation, str, dict]
            first_url='',
            task_module='',  # [str, dict]

    ):
        self.page_list = self.__check(page_list)
        self.next_page = self.__check(next_page)
        self.first_url = first_url
        self.task_module = task_module
        self.content = self.__check(content)

    @staticmethod
    def __check(item):
        if item is None:
            return ParamsPreparation()
        if isinstance(item, str):
            item = json.loads(item)
        return item if isinstance(item, ParamsPreparation) else ParamsPreparation(**item)


class ParamsPreparation(Base):
    """参数配制"""

    def __init__(
            self,
            module_name='',
            module_para: dict = None,
            **kwargs
    ):
        """

        :param module_name: 运行的类名
        :param module_para: 运行中的参数
            {
                'list_tag': { 解析数据中选择的标签还  这里面的根据爬虫解析中设计
                    'type':'soup',  # 用什么解析
                    'method':'select', ' 解析的方法
                    tag': 'ul[class="news_lb"] > li > a'  选择的标签
                }
            }
        """
        self.module_para = module_para
        self.module_name = module_name
        self.kwargs = kwargs


if __name__ == '__main__':
    model = ConfigureModel()

    print(model.copy())
    print()
