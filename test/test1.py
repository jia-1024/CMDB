# -*- coding:utf-8 -*-

# 字符串映射导入模块
c = __import__('test2')

# 动态获取属性
d = getattr(c, 'a')

print(d())



