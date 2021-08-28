# -*- coding: utf-8 -*-
# @Time    : 2018/10/9 10:35 AM
# @Author  : Joe
# @Site    :
# @File    : ansible_api.py
# @Software: PyCharm
# @function: call ansible api

from collections import namedtuple

from ansible import constants
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
# ansible >= 2.8版本需要上下文来处理options
from ansible import context
from ansible.module_utils.common.collections import ImmutableDict


# InventoryManager类,管理主机组和主机相关信息
# loader:实例对象是以什么方式来读取资产配置文件
# source：资产配置文件的路径，可以是绝对路径，也可以是相对路径


class AdhocResultsCollector(CallbackBase):
    """rewrite  ad-hoc callbackbase"""

    def __init__(self, *args, **kwargs):
        super(AdhocResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.host_failed[result._host.get_name()] = result


class PlaybookResultsCollector(CallbackBase):
    """rewrite playbook callbackbase"""
    CALLBACK_VERSION = 2.0

    def __init__(self, *args, **kwargs):
        super(PlaybookResultsCollector, self).__init__(*args, **kwargs)
        self.task_ok = {}
        self.task_unreachable = {}
        self.task_failed = {}
        self.task_skipped = {}
        self.task_status = {}

    def v2_runner_on_unreachable(self, result):
        self.task_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result):
        self.task_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.task_failed[result._host.get_name()] = result

    def v2_runner_on_skipped(self, result):
        self.task_skipped[result._host.get_name()] = result

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            # print(stats.summarize(h))
            t = stats.summarize(h)
            self.task_status[h] = {
                'ok': t['ok'],
                'failures': t['failures'],
                'unreachable': t['unreachable'],
                'changed': t['changed'],
                'skipped': t['skipped']
            }


class AnsibleApi_v2(object):
    """
    call ansible execute modules
    """

    def __init__(self, rediskey=None, logid=None, private_key_file=None):
        # self.resource = resource
        self.inventory = None
        self.variable_manage = None
        self.loader = None
        # self.options = None
        self.passwords = None
        self.callback = None
        self.__initializeDate()
        self.results_raw = {}
        self.redisKey = rediskey
        self.logId = logid
        # self.private_key_file = private_key_file

    def __initializeDate(self):
        """
        初始化ansible option
        :return:
        """
        self.loader = DataLoader()
        # ansible >= 2.8 api为cli构建，改为利用上下文对象来设置某些选项
        context.CLIARGS = ImmutableDict(
            connection='smart',
            module_path=None,
            forks=10,
            timeout=60,
            remote_user='root',
            ask_pass=True,
            private_key_file=None,
            ssh_common_args='-o StrictHostKeyChecking=no',
            ssh_extra_args='-o StrictHostKeyChecking=no',
            sftp_extra_args=None,
            scp_extra_args=None,
            become=True,
            become_method="sudo",
            become_user='root',
            ask_value_pass=False,
            verbosity=3,
            check=False,
            listhosts=None,
            listtasks=None,
            listtags=None,
            syntax=None,
            diff=True,
            start_at_task=None)

        # self.passwords = dict(sshpass=None, becomepass=None)
        self.passwords = dict()
        self.inventory = InventoryManager(
            loader=self.loader, sources='../../hosts', )
        self.variable_manage = VariableManager(
            loader=self.loader, inventory=self.inventory)

    def adh_model(
            self,
            hostip,
            group,
            port,
            sshuser,
            password,
            phpbin,
            mysqladdress,
            mysqluser,
            mysqlpassword,
            shop_version,
            vhost_path,
            mongodbaddress,
            mongodbuser,
            mongodbpassword,
            subdomain,
            module_name,
            module_args,
            fastcgi_pass,
            *args,
            **kwargs):
        """
        run module from ansible ad-hoc
        :param hostip: 主机列表
        :param module_name: ansible模块名
        :param module_args: ansible模块参数
        :return: result
        """
        # 构建数据模型
        self.inventory.add_group(group=group)
        self.inventory.add_host(host=hostip, port=port, group=group)
        hosts = self.inventory.get_host(hostname=hostip)
        # self.variable_manage.set_host_variable(
        #     host=hosts, varname="ansible_ssh_pass", value=password)
        # self.variable_manage.extra_vars = {"phpbin": phpbin}
        vars = {
            'ansible_ssh_host': hostip,
            "phpbin": phpbin,
            "ansible_user": sshuser,
            "ansible_ssh_pass": password}
        self.variable_manage.extra_vars.update(**vars)
        print(self.variable_manage.get_vars(host=hosts))
        play_source = dict(
            name='ansible play',
            hosts=hostip,
            gather_facts='no',
            tasks=[dict(action=dict(module=module_name, args=module_args))]
        )

        play = Play().load(
            play_source,
            variable_manager=self.variable_manage,
            loader=self.loader)
        tqm = None

        self.callback = AdhocResultsCollector()
        import traceback
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manage,
                loader=self.loader,
                # options=self.options,
                passwords=self.passwords,
                stdout_callback="minimal",
            )
            tqm._stdout_callback = self.callback
            constants.HOST_KEY_CHECKING = False
            print(tqm.run(play))

        except Exception as err:
            print(traceback.print_exc())
        finally:
            if tqm is not None:
                tqm.cleanup()

    def playbookrun(self, *args, **kwargs):
        """playbook runner"""
        self.callback = PlaybookResultsCollector()
        # 构建数据模型
        self.inventory.add_group(group=kwargs["group"])
        self.inventory.add_host(host=kwargs["domain"], port=kwargs["port"],
                                group=kwargs["group"])

        self.variable_manage.extra_vars.update(**kwargs)
        playbook = PlaybookExecutor(
            playbooks=kwargs["playbook_path"],
            inventory=self.inventory,
            variable_manager=self.variable_manage,
            loader=self.loader,
            passwords=self.passwords)
        playbook._tqm._stdout_callback = self.callback
        constants.HOST_KEY_CHECKING = False  # 关闭第一次使用ansible连接客户端时输入命令
        # print(self.variable_manage.get_vars(host=hosts))
        playbook.run()

    def get_model_result(self):
        self.results_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
        for host, result in self.callback.host_ok.items():
            self.results_raw['success'][host] = result._result
        for host, result in self.callback.host_failed.items():
            self.results_raw['failed'][host] = result._result
        for host, result in self.callback.host_unreachable.items():
            self.results_raw['unreachable'][host] = result._result
        return self.results_raw

    def get_playbook_result(self):
        self.results_raw = {
            'skipped': {},
            'failed': {},
            'ok': {},
            'status': {},
            'unreachable': {},
            'changed': {}}
        for host, result in self.callback.task_ok.items():
            # self.results_raw['ok'][host] = result._result
            self.results_raw['ok'] = result._result
        for host, result in self.callback.task_failed.items():
            self.results_raw['failed'] = result._result
        for host, result in self.callback.task_status.items():
            self.results_raw['status'] = result
        for host, result in self.callback.task_skipped.items():
            self.results_raw['skipped'] = result._result
        for host, result in self.callback.task_unreachable.items():
            self.results_raw['unreachable'] = result._result
        return self.results_raw
