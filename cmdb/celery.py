# -*- coding: utf-8 -*-
# @Time     : 2020/3/12 11:52 PM
# @Author   : Joe
# @Site     :
# @File     : celery.py
# @Software : PyCharm
# @function :

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms
from celery.schedules import crontab
from cmdb import celeryconfig
from celery.utils.log import get_task_logger
from celery.app.task import Task
from celery.result import AsyncResult
import datetime
from datetime import timedelta


celery_logger = get_task_logger(__name__)
# set the default django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cmdb.settings')

app = Celery('cmdb')
# app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object(celeryconfig)
app.autodiscover_tasks()

platforms.C_FORCE_ROOT = True


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# def ansible_playbook_api_29(self, tid, playbooks, extra_vars, **kwargs):
#     if isinstance(playbooks, str):
#         playbooks = ['playbooks/%s' % playbooks]
#     task_id = "AnsibleExec_%s" % datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
#     playbooks = ['../test_debug.yml', ]
#     sources = '../hosts'
#     extra_vars = {'content': '这个参数从外部传入'}
#     ansibleV3.ansibleplaybookapi(task_id, playbooks, sources, extra_vars)
#
#
# if __name__ == '__main__':
#     app.worker_main()
