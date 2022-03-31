# -*- coding: utf-8 -*-
# @Time     : 2019/10/18 5:07 PM
# @Author   : Joe
# @Site     :
# @File     : urls.py
# @Software : PyCharm
# @function : xxxx

from django.urls import path
from webssh import views

app_name = 'webssh'
urlpatterns = [
    path('', views.index, name='index')
]
