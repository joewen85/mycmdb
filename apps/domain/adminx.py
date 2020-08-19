# -*- coding: utf-8 -*-
# @Time     : 2020/8/19 11:34 AM
# @Author   : Joe
# @Site     :
# @File     : adminx.py
# @Software : PyCharm
# @function :

import xadmin
from xadmin import views

from .models import DomainDetail


class DomainDetailAdmin(object):
    list_display = ('domain', 'is_blacklist')
    search_fields = ('domain', 'is_blacklist')
    list_filter = ('domain', 'is_blacklist')


xadmin.site.register(DomainDetail, DomainDetailAdmin)
