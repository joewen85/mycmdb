# -*- coding: utf-8 -*-
# @Time    : 2018-12-13 16:16
# @Author  : Joe
# @Site    :
# @File    : zabbix_api.py
# @Software: PyCharm
# @function: xxxxx

import json
from urllib import request


class Zabbixapi:
    """
    add\modify\delete asset to zabbix
    """

    def requestjson(self, url, datas):
        data = json.dumps(datas).encode('utf-8')
        req = request.Request(url, data, {"Content-Type": "application/json-rpc"})
        response = request.urlopen(req)
        output = response.read().decode('utf-8')
        output = json.loads(output)
        try:
            result = output['result']
        except:
            result = output['error']['data']
        return result

    def authenticate(self, url, username, password):
        datas = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": username,
                "password": password
            },
            "id": 1
        }
        idvalue = self.requestjson(url, datas)
        return idvalue

    def get_groups(self, url, authid, groupname):
        datas = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": ['groupid', 'name'],
            },
            "auth": authid,
            "id": '1'
        }
        groups = self.requestjson(url, datas)
        for group in groups:
            if groupname == group['name']:
                groupid = group['groupid']
                return groupid

    def get_hosts(self, url, authid, hostname):
        datas = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": ["hostid", "host"]
            },
            "auth": authid,
            "id": 1
        }
        hosts = self.requestjson(url, datas)
        for host in hosts:
            if hostname == host['host']:
                hostid = host['hostid']
                return hostid

    def create_host(self, *args, **kwargs):
        datas = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": kwargs['hostname'],
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": kwargs['ipaddress'],
                        "dns": "",
                        "port": "10050"
                    }
                ],
                "groups": kwargs['groups'],
                "templates": kwargs['templates'],
            },
            "auth": kwargs['authid'],
            "id": 1
        }
        result = self.requestjson(kwargs['url'], datas)
        return result

    def get_template(self, url, authid, templatename):
        datas = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": ['host', 'temploateid'],
            },
            "auth": authid,
            "id": 1
        }
        templates = self.requestjson(url, datas)
        for template in templates:
            if templatename in template['host']:
                templateid = template['templateid']
                return templateid


# if __name__ == '__main__':
#     groupnames_list = [
#         'yunzhong-env',
#         'aliyun',
#     ]
#     templatenames_list = [
#         'Template Linux DiskIO active_mode',
#         'Template OS Linux active_mode',
#         'Template ICMP Ping',
#         'Template App HTTP Service',
#         'php-fpm status_active-mode',
#         'Percona MySQL Server Template_activemode',
#         'nginx_status_active-mode',
#         'mtr active_mode',
#         'getsshport_active',
#     ]
#     hostname = 'abc.com'
#     ipaddress = '1.2.3.4'
#     zb = Zabbixapi()
#     authid = zb.authenticate(url, username, password)
#     print('authenticate id : %s' % authid)
#     groupsid_list = []
#     for groupname_list in groupnames_list:
#         groupid = zb.get_groups(url, authid, groupname_list)
#         groupsid_list.append({"groupid": groupid})
#
#     templatesid_list = []
#     for templatename_list in templatenames_list:
#         templateid = zb.get_template(url, authid, templatename_list)
#         templatesid_list.append({"templateid": templateid})
#
#     result = zb.create_host(url=url, authid=authid, hostname=hostname, ipaddress=ipaddress, groups=groupsid_list, templates=templatesid_list)
#
