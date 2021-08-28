# -*- coding: utf-8 -*-
# @Time     : 2020/12/31 10:50 AM
# @Author   : Joe
# @Site     :
# @File     : weinxin.py
# @Software : PyCharm
# @function :

import time, datetime
import requests
import json


class WeChat:
    def __init__(self, corpid, corpsecret, agentid):
        # 企业id
        self.corpid = corpid
        # 应用secret
        self.corpsecret = corpsecret
        # 应用id
        self.agentid = agentid

    def _get_access_token(self):
        token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {
            'corpid': self.corpid,
            'corpsecret': self.corpsecret
        }
        resp = requests.post(token_url, params=values)
        corp_token = json.loads(resp.text)
        return corp_token['access_token']

    def get_access_token(self):
        """
        record access_token in 2 hours
        :return: access_token
        """
        try:
            with open('log/weixin_access_key.conf', 'r') as f:
                t, access_token = f.read().split()
        except:
            with open('log/weixin_access_key.conf', 'w') as f:
                access_token = self._get_access_token()
                curr_time = time.time()
                f.write('\t'.join([str(curr_time), access_token]))
                return access_token
        else:
            curr_time = time.time()
            if 0 < curr_time - float(t) < 7205:
                return access_token
            else:
                with open('log/weixin_access_key.conf', 'w') as f:
                    access_token = self._get_access_token()
                    f.write('\t'.join([str(curr_time), access_token]))
                    return access_token

    def send_data(self, message, touser, toparty=None, totag=None):
        send_url = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=" + self.get_access_token()
        str_time = datetime.datetime.strftime(datetime.datetime.now(),
                                              '%Y-%m-%d %H:%M:%S')
        send_msg = {
            "touser": touser,
            "toparty": toparty,
            "totag": totag,
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {
                "content": "任务开始时间：" + message[
                    'start_time'] + "\n" + "结束时间：" + str_time + "\n" + "操作员：" + message['operator'] + "\n" + "队列状态：" +
                           message[
                               'task_status'] + "\n" + "任务ID:" +
                           message['task_id'] + "\n" + "任务名称：" + message[
                               'job_name'] + "\n" + "域名：" + message[
                               'domain'] + "\n" + "服务器IP：" + message[
                               'ip'] + "\n" + "任务执行状态：" + message[
                               'ansible_task_status'] + "\n" + "任务执行结果：" +
                           message[
                               'ansible_message']
            },
            "safe": 0,
            # "enable_id_trans": 0,
            # "enable_duplicate_check": 0,
            # "duplicate_check_interval": 1800
        }
        send_data = (bytes(json.dumps(send_msg), 'utf-8'))
        resp = requests.post(send_url, send_data)
        return resp.json()['errmsg']
