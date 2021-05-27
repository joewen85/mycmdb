# -*- coding: utf-8 -*-
# @Time     : 2020/3/16 11:32 PM
# @Author   : Joe
# @Site     :
# @File     : celeryconfig.py
# @Software : PyCharm
# @function :


# Import project config setting
try:
    from config import Config as CONFIG
except ImportError:
    msg = """

    Error: No config file found.

    You can run `cp config_example.py config.py`, and edit it.
    """
    raise ImportError(msg)

# celery settings
broker_url = CONFIG.CELERY_BROKER_URL
result_backend = CONFIG.CELERY_BACKEND
worker_concurrency = 2
worker_prefetch_multiplier = 16
# CELERYD_FORCE_EXECV = True
worker_max_tasks_per_child = 100
worker_disable_rate_limits = True
timezone = 'Asia/Shanghai'
result_expires = 86400
task_soft_time_limit = 600
task_time_limit = 600
broker_transport_options = {
    'visibility_timeout': 1800
}
accept_content = ['json']


