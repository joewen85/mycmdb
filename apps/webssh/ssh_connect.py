# -*- coding: utf-8 -*-
# @Time     : 2019/10/17 11:40 AM
# @Author   : Joe
# @Site     :
# @File     : ssh_connect.py
# @Software : PyCharm
# @function : call ssh function

import paramiko
from threading import Thread
from webssh.tools import get_key_obj
import socket
import json


class SSH:
    def __init__(self, websocket, message):
        self.websocket = websocket
        self.message = message

    def connect(
            self,
            host,
            user,
            password=None,
            ssh_key=None,
            port=22,
            timeout=10,
            term='xterm',
            pty_width=80,
            pty_height=24):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if ssh_key:
                key = get_key_obj(
                    paramiko.RSAKey,
                    pkey_obj=ssh_key,
                    password=password) or get_key_obj(
                    paramiko.DSSKey,
                    pkey_obj=ssh_key,
                    password=password) or get_key_obj(
                    paramiko.ECDSAKey,
                    pkey_obj=ssh_key,
                    password=password) or get_key_obj(
                    paramiko.Ed25519Key,
                    pkey_obj=ssh_key,
                    password=password)
                ssh_client.connect(
                    username=user,
                    password=password,
                    port=port,
                    pkey=key,
                    timeout=timeout,
                )
            else:
                ssh_client.connect(
                    hostname=host,
                    username=user,
                    password=password,
                    port=port,
                    timeout=timeout,
                )

            transport = ssh_client.get_transport()
            self.channel = transport.open_session()
            self.channel.get_pty(term=term, width=pty_width, height=pty_height)
            self.channel.invoke_shell()

            for i in range(2):
                recv = self.channel.recv(1024).decode('utf-8')
                self.message['status'] = 0
                self.message['message'] = recv
                message = json.dumps(self.message)
                self.websocket.send(message)

        except socket.timeout:
            self.message['status'] = 1
            self.message['message'] = 'ssh 连接超时'
            message = json.dumps(self.message)
            self.websocket.send(message)
            self.close()

    def resize_pty(self, cols, rows):
        self.channel.resize_pty(width=cols, height=rows)

    def django_to_ssh(self, data):
        try:
            self.channel.send(data)
        except:
            self.close()

    def websocket_to_django(self):
        try:
            while True:
                data = self.channel.recv(1024).decode('utf-8')
                if not len(data):
                    return
                self.message['status'] = 0
                self.message['message'] = data
                message = json.dumps(self.message)
                self.websocket.send(message)
        except:
            self.close()

    def close(self):
        self.websocket['status'] = 1
        self.message['message'] = '关闭连接'
        message = json.dumps(self.message)
        self.websocket.send(message)
        self.channel.close()
        self.websocket.close()

    def shell(self, data):
        Thread(target=self.django_to_ssh, args=(data,)).start()
        Thread(target=self.websocket_to_django).start()
