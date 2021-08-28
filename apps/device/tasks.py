# -*- coding: utf-8 -*-
# @Time     : 2020/3/13 3:12 PM
# @Author   : Joe
# @Site     :
# @File     : tasks.py
# @Software : PyCharm
# @function :

from __future__ import absolute_import
import os
# import pysnooper
import datetime

from django.db.models import F
from celery import Task
from celery import shared_task
from celery.utils.log import get_task_logger
from celery.exceptions import SoftTimeLimitExceeded

from .models import Device
from utils.cryto import RsaCrypto
from utils.weixin import WeChat
from .zabbix_api import Zabbixapi
from .ansibleapi import AnsibleApi_v2

logger = get_task_logger(__name__)

try:
    from config import Config as CONFIG
except ImportError:
    msg = """

        Error: No config file found.

        You can run `cp config_example.py config.py`, and edit it.
        """
    raise ImportError(msg)

if os.environ.get("PYTHONOPTIMIZE"):
    print("开始启动")
else:
    print(
        "环境变量问题，Celery Client启动后无法正常执行Ansible任务，\n请设置export PYTHONOPTIMIZE=1；Django环境请忽略")


class MyTask(Task):
    wc = WeChat(CONFIG.CORPID, CONFIG.CORPISECRET, CONFIG.AGENTID)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        ansible_status = ''
        ansible_message = ''
        if retval['ok'] != {} and retval['failed'] == {} and retval[
            'unreachable'] == {}:
            ansible_message = retval['ok'].get('msg', '成功')
            ansible_status = "成功"
        elif retval['failed'] != {}:
            # print(retval['failed'].get('msg'))
            ansible_message = retval['failed'].get('msg')
            ansible_status = "失败"
        elif retval['unreachable'] != {}:
            ansible_message = retval['unreachable'].get('msg')
            ansible_status = "无法连接服务器"

        send_msg = {
            "task_id": task_id,
            "job_name": kwargs['job_name'],
            "domain": kwargs['domain'],
            "ip": kwargs['ansible_ssh_host'],
            "task_status": status,
            "ansible_task_status": ansible_status,
            "ansible_message": ansible_message,
            "start_time": kwargs['start_time'],
            "operator": kwargs['operator']
        }
        self.wc.send_data(message=send_msg, touser=CONFIG.TOUSER,
                          toparty=CONFIG.TOPARTY, totag=CONFIG.TOTAG)
        # 添加部署队列和计划任务记录
        try:
            device_obj = Device.objects.get(pk=kwargs['asset_id'])
            device_obj.deploy_record.create(
                deploy_datetime=datetime.datetime.now(),
                desc=kwargs['deploy_desc'],
                operator=kwargs['operator'],
                remote_ip=kwargs['remote_ip'], jobname=kwargs['job_name'],
                result=ansible_status)
        except Exception as err:
            print(err)
        return super(MyTask, self).after_return(status, retval, task_id, args,
                                                kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('任务执行失败')
        logger.info(
            'exc: {}, task_id: {}, kwargs:{}, einfi: {}'.format(exc, task_id,
                                                                kwargs, einfo))
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print('任务正在重试')

    def on_success(self, retval, task_id, args, kwargs):
        print('任务执行成功')
        device_obj = ''
        retval_msg = retval['ok'].get('msg')
        try:
            device_obj = Device.objects.get(pk=kwargs['asset_id'])
        except Exception as err:
            print(err)
        task_path = ''.join(kwargs['playbook_path'])
        if task_path == CONFIG.PLAYBOOKPATH + "/envirment.yml" or task_path == CONFIG.PLAYBOOKPATH + "/roles/ftp/ftp.yml":
            # 写入ftp密码
            encrypt_deploy_result = RsaCrypto().encrypt(retval_msg)['message']
            device_obj.PASSWORD.update(ftppassword=encrypt_deploy_result)

        elif task_path == CONFIG.PLAYBOOKPATH + "/roles/mysql/mysql.yml":
            # 写入mysql密码
            encrypt_deploy_result = RsaCrypto().encrypt(retval_msg)['message']
            device_obj.PASSWORD.update(mysqlpassword=encrypt_deploy_result)

        elif task_path == CONFIG.PLAYBOOKPATH + "/roles/mongodb/mongodb.yml":
            # 写入mongodb密码
            encrypt_deploy_result = RsaCrypto().encrypt(retval_msg)['message']
            device_obj.PASSWORD.update(mongodbpassword=encrypt_deploy_result)

        if task_path == CONFIG.PLAYBOOKPATH + "/cronjob_queue.yml":
            """部署队列和计划任务成功后计数"""
            Device.objects.filter(hostname=device_obj.hostname).update(
                deploy_times=F('deploy_times') + 1)
        elif task_path == CONFIG.PLAYBOOKPATH + "/roles/zabbix_client/zabbix_client.yml":
            zabbix_url = CONFIG.ZABBIX_URL
            zabbix_user = CONFIG.ZABBIX_USER
            zabbix_passwd = CONFIG.ZABBIX_PASSWD

            groupnames_list = [
                kwargs['group'],
                kwargs['isp']
            ]
            templatenames_list = [
                'Template Linux DiskIO active_mode',
                'Template OS Linux active_mode',
                'Template ICMP Ping',
                'Template App HTTP Service',
                'php-fpm status_active-mode',
                'Template App MySQL_active-mode',
                'nginx_status_active-mode',
                'mtr active_mode',
                'getsshport_active',
                'Custom TCP Connect Stat_active',
                'Template App Redis_active',
            ]

            zb = Zabbixapi()
            authid = zb.authenticate(zabbix_url, zabbix_user, zabbix_passwd)
            groupsid_list = []
            for groupname_list in groupnames_list:
                groupid = zb.get_groups(zabbix_url, authid, groupname_list)
                groupsid_list.append({"groupid": groupid})
            templatesid_list = []
            for templatename_list in templatenames_list:
                templateid = zb.get_template(zabbix_url, authid,
                                             templatename_list)
                templatesid_list.append({"templateid": templateid})
            zb.create_host(url=zabbix_url, authid=authid,
                           hostname=device_obj.hostname,
                           ipaddress=device_obj.ipaddress,
                           groups=groupsid_list, templates=templatesid_list)

        logger.info(
            'task id:{} , retval:{}, arg:{} , kwargs:{} successful !'.format(
                task_id, retval, args, kwargs))
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)


@shared_task(base=MyTask)
# @pysnooper.snoop('log/debug_async.log')
def deploy_task(**kwargs):
    print("任务函数进行中。。。。。。。。")
    print("")
    try:
        runningjob = AnsibleApi_v2()
        runningjob.playbookrun(**kwargs)
        task_result = runningjob.get_playbook_result()
        return task_result
    except SoftTimeLimitExceeded:
        print("处理任务超时!!!!")


def get_task_status(task_id):
    task = deploy_task.AsyncResult(task_id)

    status = task.state
    progress = 0

    if status == 'SUCCESS':
        progress = 100
    elif status == 'FAILURE':
        progress = 0
    elif status == 'PROGRESS':
        progress = task.info['progress']
    return {'status': status, 'progress': progress}
