# -*- coding: utf-8 -*-
# @Time     : 2022/4/19 8:43 PM
# @Author   : Joe
# @Site     :
# @File     : tools_test.py
# @Software : PyCharm
# @function : xxxx
import os

from collections import defaultdict

a = defaultdict(lambda: 10)

print(a[1], a[5])
print(os.env)
print(os.path)
print(defaultdict())
print(f"test output")