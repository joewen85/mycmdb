# -*- coding: utf-8 -*-
# @Time     : 2019/10/18 5:03 PM
# @Author   : Joe
# @Site     : 
# @File     : routing.py
# @Software : PyCharm
# @function : xxxx

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from webssh.websocket import WebSSH

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('webssh/', WebSSH)
        ])
    )
})