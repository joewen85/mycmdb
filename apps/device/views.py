import datetime
import logging
import os
import json

from captcha.models import CaptchaStore
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import render, redirect, HttpResponseRedirect, reverse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic import View

from device.ansibleapi import AnsibleApi_v2
from device.forms import AddForm, LoginForm, CaptchaForm
from device.models import Envirment, Device, Cloudips, Jobs, Deploy_record, User

# from django.views.decorators.cache import cache_page
try:
    from config import Config as CONFIG
except ImportError:
    msg = """

        Error: No config file found.

        You can run `cp config_example.py config.py`, and edit it.
        """
    raise ImportError(msg)
from .zabbix_api import Zabbixapi

logger = logging.getLogger(__name__)
collect_logger = logging.getLogger('collect')


def ajax_val(request):
    if request.is_ajax():
        cs = CaptchaStore.objects.filter(response=request.GET['response'], hashkey=request.GET['hashkey'])
        if cs:
            json_data = {'status': 1}
        else:
            json_data = {'status': 0}
        return JsonResponse(json_data)
    else:
        json_data = {'status': 0}
        return JsonResponse(json_data)


def index(request):
    return render(request, "index.html")


class LoginView(View):
    """
    verfy login
    """

    def get(self, request):
        next = request.GET.get('next', '/')
        return render(request, "login.html", {'next': next, 'msg': ""})

    def post(self, request):
        login_form = LoginForm(request.POST)
        next = request.POST.get('next')
        if login_form.is_valid():
            username = request.POST.get('username', "")
            userpassword = request.POST.get('userpassword', "")

            user = auth.authenticate(username=username, password=userpassword)
            if user is not None:
                auth.login(request, user)
                return redirect(next)
                # return HttpResponseRedirect(next) #硬链接
            else:
                return render(request, 'login.html', {'msg': '用户名或密码不正确', 'next': next})
        else:
            return render(request, 'login.html', {'login_form': login_form.errors, 'next': next})


class LogoutView(View):
    """
    用户登出
    """

    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


@method_decorator(login_required, name='dispatch')
class AssetAdd(View):
    """
    add，modify custom asset
    """

    # @method_decorator(cache_page(60))
    def get(self, request):
        envall = Envirment.objects.all()
        ispall = Cloudips.objects.all()
        return render(request, 'asset.html', {'env_datas': envall, 'cloudisp_datas': ispall})

    def post(self, request):
        if request.method == "POST":
            form = AddForm(request.POST)
            if form.is_valid():
                domain = form.cleaned_data.get('domain')
                ipaddr = form.cleaned_data.get('ipaddress')
                username = request.POST.get('username', None)
                password = request.POST.get('password', None)
                position = form.cleaned_data.get('position')
                envirment = request.POST.get('select1', None)
                cloudips = request.POST.get('select2', None)
                customer_name = request.POST.get('customer_name', None)
                port = form.cleaned_data.get('port')
                others = request.POST.get('others', None)
                paid = request.POST.get('vers', 0)
                if Device.objects.filter(hostname=domain).exists():
                    # if get_domain.exists():
                    Device.objects.filter(hostname=domain).update(ipaddress=ipaddr, sshuser=username,
                                                                  sshpassword=password, websitepath=position,
                                                                  envirment_id=envirment, cloudips_id=cloudips,
                                                                  customer_name=customer_name, sshport=port,
                                                                  others=others, paid=paid,
                                                                  updated_at=datetime.datetime.now())
                    messages.success(request, "域名已存在，已保存其它内容")
                    redirect_url = reverse('assetlist') + '?page=1'
                    return redirect(redirect_url)
                else:
                    Device.objects.create(hostname=domain, ipaddress=ipaddr, sshuser=username, sshpassword=password,
                                          websitepath=position, sshport=port, is_maintenance=0, deploy_times=0,
                                          cloudips_id=cloudips, envirment_id=envirment, customer_name=customer_name,
                                          others=others, paid=paid)
                    messages.success(request, "保存资产成功")
                    redirect_url = reverse('assetlist') + '?page=1'
                    return redirect(redirect_url)
            else:
                return render(request, 'asset.html', {'verify_form': form.get_errors()})


@method_decorator(login_required, name='dispatch')
class AssetListView(View):
    """
    list latest 10 asset and search asset
    """

    def get(self, request):
        # all_asset_list = Device.objects.values('id', 'customer_name', 'hostname', 'ipaddress', 'created_at').order_by('-id', 'created_at')[:10]
        all_asset_lists = Device.objects.all().order_by('-pk', 'created_at')
        # 分页 每页10条数据
        paginator = Paginator(all_asset_lists, 10)
        # print(paginator.count, paginator.num_pages, paginator.page_range)
        page_range = paginator.page_range
        num_page = paginator.num_pages
        total = paginator.count
        around_count = 2
        leff_has_more = False
        right_has_more = False
        try:
            current_page = int(request.GET.get('page'))
        except Exception as e:
            messages.success(request, "请勿传入非法值")
            current_page = 1

        try:
            contacts = paginator.get_page(current_page)
        except PageNotAnInteger:
            contacts = paginator.get_page(1)
        except EmptyPage:
            contacts = paginator.get_page(num_page)

        if current_page <= around_count + 2:
            left_range = range(1, current_page)
        else:
            leff_has_more = True
            left_range = range(current_page - around_count, current_page)

        if current_page >= num_page - around_count - 1:
            right_range = range(current_page + 1, num_page + 1)
        else:
            right_has_more = True
            right_range = range(current_page + 1, current_page + around_count + 1)
        return render(request, 'asset_list.html',
                      {'contacts': contacts, 'page_range': page_range, 'current_page': current_page,
                       'num_page': num_page, 'left_range': left_range, 'right_range': right_range,
                       'left_has_more': leff_has_more, 'right_has_more': right_has_more, 'total': total, 'msg': ''})

    def post(self, request):
        search_field = request.POST.get('searcher').strip()
        if search_field:
            get_field = Device.objects.filter(
                Q(hostname=search_field) | Q(ipaddress=search_field) | Q(
                    customer_name__icontains=search_field)).order_by('-created_at', '-id')
            if get_field.exists():
                paginator = Paginator(get_field, 100)
                page_range = paginator.page_range
                num_page = paginator.num_pages
                total = paginator.count
                current_page = 1
                try:
                    contacts = paginator.get_page(current_page)
                except PageNotAnInteger:
                    contacts = paginator.get_page(1)
                except EmptyPage:
                    contacts = paginator.get_page(num_page)
                return render(request, 'asset_list.html',
                              {'contacts': contacts, 'page_range': page_range, 'current_page': current_page,
                               'num_page': num_page, 'msg': '', 'total': total})
            else:
                return render(request, 'asset_list.html', {'msg': '没有该资产信息', 'total': 0})
        else:
            messages.success(request, "请输入搜索关键字")
            redirect_url = reverse('assetlist') + '?page=1'
            return redirect(redirect_url)


@method_decorator(login_required, name='dispatch')
class AssetFuncsView(View):
    """
    asset all functions
    """

    def get(self, request, asset_id):
        if request.method == "GET":
            asset_detail = Device.objects.filter(id=asset_id)
            task_list = Jobs.objects.all()
            env_list = Envirment.objects.all()
            isp_list = Cloudips.objects.all()
            deployrec_list = Deploy_record.objects.filter(hostname=asset_id)
            # return JsonResponse({'code': 200, 'message': asset_id, 'data': asset_detail})
            return render(request, 'asset_detail.html',
                          {'asset_detail': asset_detail, 'task_list': task_list, 'env_lists': env_list,
                           'cloudisp_list': isp_list, 'deploy_records': deployrec_list})

    def post(self, request, asset_id):
        asset_id = request.POST.get('asset_id')
        domain = request.POST.get('domain', None)
        ipaddr = request.POST.get('ipaddress', None)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        position = request.POST.get('position', None)
        ftpuser = request.POST.get('ftpuser', None)
        ftppassword = request.POST.get('ftppassword', None)
        mysqladdress = request.POST.get('mysqladdress', None)
        mysqluser = request.POST.get('mysqluser', None)
        mysqlpassword = request.POST.get('mysqlpassword', None)
        envirment = request.POST.get('select_env', None)
        # envirment = request.POST.get('env', None)
        cloudips = request.POST.get('select_isp', None)
        # cloudips = request.POST.get('cloudips', None)
        customer_name = request.POST.get('customer_name', None)
        port = request.POST.get('port', None)
        job = request.POST.get('select1', None)
        others = request.POST.get('others', None)
        deploy_desc = request.POST.get('desc')
        paid = bool(request.POST.get('vers'))
        if paid:
            download_vers = 'paid'
        else:
            download_vers = 'free'
        device_obj = Device.objects.get(id=asset_id)
        operator = request.POST.get('user')
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            remote_ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            remote_ip = request.META['REMOTE_ADDR']

        # operator_id = User.objects.get(username=operator).id

        if 'assetdelete' in request.POST:
            """删除资产"""
            # Device.objects.get(pk=asset_id).delete()
            device_obj.delete()
            messages.success(request, "删除资产成功")
            redirect_url = reverse('assetlist') + '?page=1'
            return redirect(redirect_url)
        elif 'deploy' in request.POST:
            """接收post data，传入ansibleapi核心类，部署各个任务"""
            # 获取envname
            # env_name = Envirment.objects.filter(id=envirment).values("envname").first()['envname']
            # env_name = Envirment.objects.filter(describe=envirment).values("envname").first()['envname']
            # envresult = Envirment.objects.get(id=envirment)
            # envresult = Envirment.objects.get(id=device_obj.envirment__id)
            env_name = device_obj.envirment.envname

            # cloudips_name = Cloudips.objects.get(pk=device_obj.cloudips__id).cloudipsname
            cloudips_name = device_obj.cloudips.cloudipsname

            # 获取任务路径
            # j = Jobs.objects.filter(jid=job)
            # jobinfo = Jobs.objects.filter(jid=job).values("path").first()['path']
            job_obj = Jobs.objects.get(pk=job)
            jobpath = job_obj.path
            jobname = job_obj.name

            # 获取php环境路径
            # phpbin = Device.objects.filter(hostname=domain).values("envirment__phpbin").first()['envirment__phpbin']
            # phpbin = envresult.phpbin
            phpbin = device_obj.envirment.phpbin

            # 执行ansible playbook
            runningjob = AnsibleApi_v2()

            runningjob.playbookrun(playbook_path=[jobpath], domain=device_obj.hostname, hostip=device_obj.ipaddress,
                                   group=env_name, port=device_obj.sshport,
                                   sshuser=device_obj.sshuser, password=device_obj.sshpassword, phpbin=phpbin,
                                   webpath=device_obj.websitepath,
                                   download_vers=download_vers, mysql_user=device_obj.mysqluser,
                                   mysql_password=device_obj.mysqlpassword, mysql_address=device_obj.mysqladdress)

            data = runningjob.get_playbook_result()

            if jobpath == "/data/apps/mycmdb/playbooks/cronjob_queue.yml":
                """部署队列和计划任务成功后计数"""
                Device.objects.filter(hostname=device_obj.hostname).update(deploy_times=F('deploy_times') + 1)
            elif jobpath == "/data/apps/mycmdb/playbooks/roles/zabbix_client/zabbix_client.yml":
                zabbix_url = CONFIG.ZABBIX_URL
                zabbix_user = CONFIG.ZABBIX_USER
                zabbix_passwd = CONFIG.ZABBIX_PASSWD

                groupnames_list = [
                    env_name,
                    cloudips_name,
                ]
                templatenames_list = [
                    'Template Linux DiskIO active_mode',
                    'Template OS Linux active_mode',
                    'Template ICMP Ping',
                    'Template App HTTP Service',
                    'php-fpm status_active-mode',
                    'Percona MySQL Server Template_activemode',
                    'nginx_status_active-mode',
                    'mtr active_mode',
                    'getsshport_active',
                    'Custom TCP Connect Stat_active',
                ]

                zb = Zabbixapi()
                authid = zb.authenticate(zabbix_url, zabbix_user, zabbix_passwd)
                groupsid_list = []
                for groupname_list in groupnames_list:
                    groupid = zb.get_groups(zabbix_url, authid, groupname_list)
                    groupsid_list.append({"groupid": groupid})

                templatesid_list = []
                for templatename_list in templatenames_list:
                    templateid = zb.get_template(zabbix_url, authid, templatename_list)
                    templatesid_list.append({"templateid": templateid})
                zb.create_host(url=zabbix_url, authid=authid, hostname=device_obj.hostname,
                               ipaddress=device_obj.ipaddress,
                               groups=groupsid_list, templates=templatesid_list)

            if data['ok']:
                deploy_result = data['ok'].get('msg')
            elif data['failed']:
                deploy_result = data['failed'].get('stderr')
            elif data['unreachable']:
                deploy_result = data['unreachable'].get('msg')

            if jobpath == CONFIG.PLAYBOOKPATH + "/envirment.yml" or jobpath == CONFIG.PLAYBOOKPATH + "/roles/ftp/ftp.yml":
                # 写入ftp密码
                device_obj.ftppassword = deploy_result
                device_obj.save()
                deploy_result = "ftp user: www ftp password: " + str(deploy_result)
            elif jobpath == CONFIG.PLAYBOOKPATH + "/roles/mysql/mysql.yml":
                device_obj.mysqlpassword = deploy_result
                device_obj.save()
                deploy_result = "mysql root password: " + str(deploy_result)

            # 添加部署队列和计划任务记录
            Deploy_record.objects.create(deploy_datetime=datetime.datetime.now(), desc=deploy_desc,
                                         hostname=device_obj, operator=request.user.username, remote_ip=remote_ip,
                                         jobname=jobname, result=deploy_result)
            print(json.dumps(data, indent=4))

            return render(request, "deploy_result.html",
                          {"data": data, "ipaddress": device_obj.ipaddress, "domain": device_obj.hostname})
        else:
            """修改资产"""
            if 'assetupdate' in request.POST:
                Device.objects.filter(id=asset_id).update(ipaddress=ipaddr, hostname=domain, sshuser=username,
                                                          sshpassword=password, websitepath=position,
                                                          envirment_id=envirment, cloudips_id=cloudips,
                                                          customer_name=customer_name, sshport=port,
                                                          others=others, paid=paid, updated_at=datetime.datetime.now(),
                                                          ftpuser=ftpuser, ftppassword=ftppassword,
                                                          mysqladdress=mysqladdress, mysqluser=mysqluser,
                                                          mysqlpassword=mysqlpassword)
                messages.success(request, "修改内容成功")
                return redirect(reverse('assetdetail', kwargs={'asset_id': asset_id}))


class AnsibleViewPublic(View):
    """
    接收post data，传入ansibleapi核心。并将内容入库
    """

    def get(self, request):
        env_datas = Envirment.objects.all()
        cloudips_datas = Cloudips.objects.all()

        # 判断用户是否登陆，登陆显示所有任务，anonymous用户只显示10条
        if request.user.is_authenticated:
            jobs = Jobs.objects.all()
        else:
            jobs = Jobs.objects.filter(pk__lte=11)

        captcha_form = CaptchaForm()
        return render(request, 'deploy_public.html',
                      {'env_datas': env_datas, 'cloudips_datas': cloudips_datas, 'jobs': jobs,
                       'captcha_form': captcha_form, 'verify_form': {}})

    def post(self, request, *args, **kwargs):
        verify_form = AddForm(request.POST)
        captcha_form = CaptchaForm(request.POST)

        if verify_form.is_valid() and captcha_form.is_valid():
            domain = verify_form.cleaned_data.get('domain')
            ipaddr = verify_form.cleaned_data.get('ipaddress')
            username = verify_form.cleaned_data.get('username')
            password = verify_form.cleaned_data.get('password')
            position = verify_form.cleaned_data.get('position')
            mysqladdress = request.POST.get('mysqladdress', None)
            mysqluser = request.POST.get('mysqluser', None)
            mysqlpassword = request.POST.get('mysqlpassword', None)
            envirment = request.POST.get('select1', None)
            cloudips = request.POST.get('select2', None)
            customer_name = verify_form.cleaned_data.get('customer_name')
            port = verify_form.cleaned_data.get('port')
            job = request.POST.get('select3', None)
            others = request.POST.get('others', None)
            deploy_desc = request.POST.get('desc', None)
            # download_vers = request.POST.get('vers', 'free')
            download_vers = 'free'
            operator = request.POST.get('user')
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                remote_ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                remote_ip = request.META['REMOTE_ADDR']

            # operator_id = User.objects.get(username=operator).id

            # 获取envname
            envresult = Envirment.objects.get(id=envirment)
            env_name = envresult.envname

            # 获取任务路径
            job_obj = Jobs.objects.get(pk=job)
            jobpath = job_obj.path
            jobname = job_obj.name
            # print(jobinfo)

            # 获取php环境路径
            phpbin = envresult.phpbin

            data = {
                'hostname': domain, 'ipaddress': ipaddr, 'sshuser': username, 'sshpassword': password,
                'websitepath': position,
                'envirment_id': envirment, 'cloudips_id': cloudips, 'customer_name': customer_name, 'sshport': port,
                'others': others, 'mysql_user': mysqluser, 'mysql_password': mysqlpassword,
                'mysql_address': mysqladdress
            }

            # 公共部署判断服务器是否部署多次
            asset_objs = Device.objects.filter(ipaddress=ipaddr)
            if len(asset_objs) >= 2:
                messages.error(request, '服务器不能部署太多站点。！')
                return redirect(reverse('deploy_public'))

            # 判断数据库中是否有记录，没有则创建，有则修改
            try:
                custom_asset, created = Device.objects.update_or_create(hostname=domain, defaults=data)
            except Exception as e:
                print("数据异常！请联系管理员")

            times = custom_asset.deploy_times
            weiqingshop_times = custom_asset.deploy_weiqingshop_times
            frameworkshop_times = custom_asset.deploy_frameworkshop_times

            # limit queue and cronjob check
            if times > 5:
                messages.error(request, '免费部署计划任务和队列次数已用尽请联系管理员。！！！')
                return redirect(reverse('deploy_public'))

            # limit weiqingshop check
            elif weiqingshop_times > 1:
                messages.error(request, '免费部署次数已用尽请联系管理员。！！！')
                return redirect(reverse('deploy_public'))

            # limit frameworkshop check
            elif frameworkshop_times > 1:
                messages.error(request, '免费部署次数已用尽请联系管理员。！！！')
                return redirect(reverse('deploy_public'))

            # 执行ansible playbook
            runningjob = AnsibleApi_v2()
            runningjob.playbookrun(playbook_path=[jobpath], domain=domain, hostip=ipaddr, group=env_name,
                                   port=port, sshuser=username, password=password, phpbin=phpbin,
                                   webpath=position, download_vers=download_vers, mysql_user=mysqluser,
                                   mysql_password=mysqlpassword, mysql_address=mysqladdress)

            data = runningjob.get_playbook_result()

            # 累计部署记录
            if jobname == '部署队列和计划任务':
                Device.objects.filter(hostname=domain).update(deploy_times=F('deploy_times') + 1)
            elif jobname == '部署微擎或商城(微擎框架)':
                Device.objects.filter(hostname=domain).update(
                    deploy_weiqingshop_times=F('deploy_weiqingshop_times') + 1)
            elif jobname == '部署框架商城(芸众框架)':
                Device.objects.filter(hostname=domain).update(
                    deploy_frameworkshop_times=F('deploy_frameworkshop_times') + 1)

            # 获取结果
            if data['ok']:
                deploy_result = data['ok'].get('msg')
            elif data['failed']:
                deploy_result = data['failed'].get('stderr')
            elif data['unreachable']:
                deploy_result = data['unreachable'].get('msg')

            # 添加部署记录
            Deploy_record.objects.create(deploy_datetime=datetime.datetime.now(), hostname=custom_asset,
                                         operator=request.user.username, remote_ip=remote_ip, desc=deploy_desc,
                                         jobname=jobname, result=deploy_result)
            print(json.dumps(data, indent=4))
            return render(request, "deploy_result.html", {"data": data, "domain": domain})
        else:
            return render(request, "deploy_public.html",
                          {'verify_form': verify_form.get_errors(), 'captcha_form': captcha_form.errors,
                           'descript_form': "error"})


@login_required
def shop_download(request):
    ver = request.GET.get('ver')
    user = request.user.username
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        remote_ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        remote_ip = request.META['REMOTE_ADDR']
    file_path = '/data/apps/mycmdb/playbooks/roles/shop/files/{}'.format(ver)
    try:
        file_size = os.path.getsize(file_path)
        response = HttpResponse()
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Encoding'] = 'unicode'
        response['Content-Length'] = '{}'.format(file_size)
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(ver)
        response['X-Accel-Redirect'] = "/protect_files/{}".format(ver)
        msg = " ".join([user, remote_ip, ':download_file with', ver])
        collect_logger.info(msg)
        return response
    except Exception as e:
        msg = " ".join([user, remote_ip, str(e)])
        collect_logger.info(msg)
        return HttpResponse(e)
