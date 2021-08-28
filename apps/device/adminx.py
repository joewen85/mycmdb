# -*- coding: utf-8 -*-
# auther: Joe wen
# date: 2018/8/31 下午3:42

import xadmin
from xadmin import views

from .models import Cloudips, Envirment, Device, Jobs, Deploy_record, Password_record


class GlobalSettings(object):
    site_title = '芸众后台管理系统'
    site_footer = '芸众管理系统'
    menu_style = 'accordion'


class BaseSetting(object):
    enable_themes = True  # 开启主题使用
    use_bootswatch = True


class CloudipsAdmin(object):
    list_display = ('cloudipsname', 'describe', 'created_at', 'updated_at')
    search_fields = ('cloudipsname', 'describe',)
    list_filter = ('cloudipsname', 'describe',)


class EnvirmentAdmin(object):
    list_display = ('envname', 'describe', 'fastcgi_pass', 'created_at', 'updated_at')
    search_fields = ('envname', 'describe',)
    list_filter = ('envname', 'describe')
    model_icon = 'fa fa-bug fa-fw'


class DeviceAdmin(object):
    list_display = ('customer_name', 'hostname', 'ipaddress', 'envirment', 'cloudips', 'deploy_times', 'is_maintenance',
                    'maintenance_duration',
                    'created_at', 'updated_at',)
    search_fields = (
    'customer_name', 'hostname', 'ipaddress', 'is_maintenance', 'envirment__describe', 'cloudips__describe')
    list_filter = ('customer_name', 'hostname', 'ipaddress', 'envirment', 'cloudips', 'is_maintenance', 'deploy_times')
    list_per_page = 10
    list_editable = ['ipaddress', 'hostname']
    model_icon = 'fa fa-book fa-fw'


class JobAdmin(object):
    list_display = ('name', 'describe', 'path')
    search_fields = ('name',)
    list_filter = ('name',)
    model_icon = 'fa fa-linux fa-fw'


class Deploy_recordAdmin(object):
    list_display = ('operator', 'remote_ip', 'hostname', 'deploy_datetime', 'desc', 'jobname')
    search_fields = ('operator', 'hostname__hostname')
    list_filter = ('hostname','jobname')
    list_per_page = 10
    model_icon = 'fa fa-archive fa-fw'


class Password_recordAadmin(object):
    list_display = ('ipaddress', 'sshpassword', 'ftppassword', 'mysqlpassword')
    # search_fields = ('server_ip__iptabless')
    list_per_page = 10


xadmin.site.register(Cloudips, CloudipsAdmin)
xadmin.site.register(Envirment, EnvirmentAdmin)
xadmin.site.register(Device, DeviceAdmin)
xadmin.site.register(Jobs, JobAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
xadmin.site.register(Deploy_record, Deploy_recordAdmin)
xadmin.site.register(Password_record, Password_recordAadmin)
