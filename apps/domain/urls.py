# -*- coding: utf-8 -*-
# @Time    : 2019-08-09 22:38
# @Author  : Joe
# @Site    :
# @File    : urls.py
# @Software: PyCharm
# @function: xxxxx

from django.urls import path
from domain.views import DomainView, BlackListList, BlackListDetail
from rest_framework.documentation import include_docs_urls

API_TITLE = 'devops api documentation'
API_DESCRIPTION = 'devops'

urlpatterns = [
    path('', DomainView.as_view()),
    path('blacklist/', BlackListList.as_view(), name='blacklist_list'),
    path('blacklist/<int:pk>', BlackListDetail.as_view(), name='blacklist_list'),
    path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION, authentication_classes=[], permission_classes=[]))
]
