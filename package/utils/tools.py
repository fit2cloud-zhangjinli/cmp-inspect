# _*_ coding: utf-8 _*_
"""
Time:     2023/3/27 下午5:39
Author:   JinLi
Version:  V 0.1
File:     tools.py.py
"""

from jinja2 import Environment, FileSystemLoader
import datetime

# 时间
now = datetime.datetime.now()
start_time = now.strftime("%a, %d %b %Y %H:%M:%S")
end_time = now.strftime("%a, %d %b %Y %H:%M:%S")

# 创建 Jinja2 环境
env = Environment(loader=FileSystemLoader('../templates'))

# 加载模板
template = env.get_template('cmp_report.html')

# 渲染模板
# data1 = {'name': 'John', 'age': 30, 'now_time': now_time}
# data2 = {'name2': '2John', 'age2': 230}
# result = template.render(**data1, **data2)

# 输出结果
# print(result)
