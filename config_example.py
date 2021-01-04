# -*- coding: utf-8 -*-
# @Time    : 2019-03-05 14:36
# @Author  : Joe
# @Site    :
# @File    : config_example.py
# @Software: PyCharm
# @function: set paraments


import os

BASE_DIR = os.getcwd()


class Config:
    # Django security setting, if your disable debug model, you should setting that
    ALLOWED_HOSTS = ['*']

    SECRET_KEY = os.environ.get("SECRET_KEY")
    # Development env open this, when error occur display the full process track, Production disable it
    DEBUG = os.environ.get("DEBUG") or False
    # DEBUG, INFO, WARNING, ERROR, CRITICAL can set. See https://docs.djangoproject.com/en/1.10/topics/logging/
    LOG_LEVEL = os.environ.get("LOG_LEVEL") or 'WARNING'
    LOG_DIR = os.path.join(BASE_DIR, 'log')

    APP_ENV = os.environ.get("APP_ENV") or 'develop'

    # MySQL setting like:
    DB_ENGINE = os.environ.get("DB_ENGINE") or 'mysql'
    DB_HOST = os.environ.get("DB_HOST") or '127.0.0.1'
    DB_PORT = os.environ.get("DB_PORT") or 3306
    DB_USER = os.environ.get("DB_USER") or 'root'
    DB_PASSWORD = os.environ.get("DB_PASSWORD") or '123456'
    DB_NAME = os.environ.get("DB_NAME") or 'xxx'

    # When Django start it will bind this host and port
    # ./manage.py runserver 127.0.0.1:8000
    HTTP_BIND_HOST = '0.0.0.0'
    HTTP_LISTEN_PORT = 8000

    CACHE_LOCATION = os.environ.get("CACHE_LOCATION") or 'redis://:password@ip:6379/1'
    CACHE_TIMEOUT = os.environ.get("CACHE_TIMEOUT") or 60

    SESSION_SAVE = os.environ.get("SESSION_SAVE") or 'redis://:password@ip:6379/2'
    CHANNEL_LAYER_REDIS = os.environ.get("CHANNEL_LAYER_REDIS") or 'redis://:password@ip:6379/0'

    # zabbix config setting
    ZABBIX_URL = "https://xxxxx/api_jsonrpc.php"
    ZABBIX_USER = "xxxx"
    ZABBIX_PASSWD = "xxxxx"

    # domain api config
    API_HOSTIP = ''
    API_GROUP = ''
    API_SSHUSER = ''
    API_SSHPASSWORD = ''
    API_WEBPATH = ''

    # Celery setting
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKEN") or 'redis://:xxx@127.0.0.1:6379/3'

    # playbook path
    PLAYBOOKPATH = BASE_DIR + "/playbook"

    # public_key
    PUBLIC_KEY = ''''''

    # private_key
    PRIVATE_KEY = ''''''

    # TOKEN
    TOKEN = ''

    # celery config
    CELERY_BROKER_URL = ''
    CELERY_RESULT_BACKEND = ''
    CELERY_MAX_TASKS_PER_CHILD = ''
    CELERYD_CONCURRENCY = ''

    # wecom secret
    CORPID = ''
    CORPISECRET = ''
    AGENTID = ''
    TOUSER = ''
    TOPARTY = ''
    TOTAG = ''
