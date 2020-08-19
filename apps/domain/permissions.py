# -*- coding: utf-8 -*-
# @Time     : 2020/8/19 4:06 PM
# @Author   : Joe
# @Site     :
# @File     : permissions.py
# @Software : PyCharm
# @function :


from rest_framework import permissions

# Import project config setting
try:
    from config import Config as CONFIG
except ImportError:
    msg = """

    Error: No config file found.

    You can run `cp config_example.py config.py`, and edit it.
    """
    raise ImportError(msg)


class IsTokenOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method is permissions.SAFE_METHODS:
            return True
        return request.META.get('HTTP_TOKEN') == CONFIG.TOKEN
